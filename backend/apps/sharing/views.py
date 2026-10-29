from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import ShareLink, ShareTargetType
from .serializers import ShareLinkSerializer
from apps.workspaces.models import Workspace
from apps.albums.models import Album, AlbumAsset
from apps.albums.serializers import AlbumSerializer, AlbumAssetSerializer
from apps.folders.serializers import FolderSerializer
from apps.files.serializers import FileAssetSerializer
from apps.activity.models import ActivityLog

class ShareLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ShareLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ShareLink.objects.filter(workspace__memberships__user=user)
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs.select_related('album', 'folder', 'file_asset')

    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = Workspace.objects.get(id=workspace_id, memberships__user=self.request.user)
        share_link = serializer.save(workspace=workspace)
        ActivityLog.objects.create(
            workspace=workspace,
            user=self.request.user,
            action='CREATE_SHARE_LINK',
            target_type='SHARE',
            target_id=str(share_link.id),
            description=f"Created share link for {share_link.target_type}: {share_link.title or share_link.token}"
        )


class PublicShareView(APIView):
    """
    Public endpoint for client galleries and shared links.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            link = ShareLink.objects.select_related('album', 'folder', 'file_asset', 'workspace').get(token=token, is_active=True)
        except ShareLink.DoesNotExist:
            return Response({'detail': 'Share link not found or inactive.'}, status=status.HTTP_404_NOT_FOUND)

        if link.is_expired:
            return Response({'detail': 'This share link has expired.'}, status=status.HTTP_410_GONE)

        # Check password protection
        if link.is_password_protected:
            password = request.headers.get('X-Share-Password') or request.query_params.get('password')
            if not password or not link.verify_password(password):
                return Response({
                    'is_password_protected': True,
                    'title': link.title or 'Protected Client Gallery',
                    'target_type': link.target_type,
                    'requires_password': True
                }, status=status.HTTP_401_UNAUTHORIZED)

        # Increment view count
        ShareLink.objects.filter(id=link.id).update(view_count=F('view_count') + 1)

        response_data = {
            'token': link.token,
            'title': link.title,
            'target_type': link.target_type,
            'allow_downloads': link.allow_downloads,
            'allow_favorites': link.allow_favorites,
            'created_at': link.created_at,
            'workspace_name': link.workspace.name,
        }

        if link.target_type == ShareTargetType.ALBUM and link.album:
            album_assets = AlbumAsset.objects.filter(album=link.album).select_related('file_asset')
            response_data['album'] = AlbumSerializer(link.album).data
            response_data['assets'] = AlbumAssetSerializer(album_assets, many=True).data
        elif link.target_type == ShareTargetType.FOLDER and link.folder:
            files = link.folder.files.filter(is_deleted=False)
            response_data['folder'] = FolderSerializer(link.folder).data
            response_data['files'] = FileAssetSerializer(files, many=True).data
        elif link.target_type == ShareTargetType.FILE and link.file_asset:
            response_data['file'] = FileAssetSerializer(link.file_asset).data

        return Response(response_data)

    def post(self, request, token):
        """
        Handle client interactions such as toggling favorites or recording downloads.
        """
        try:
            link = ShareLink.objects.get(token=token, is_active=True)
        except ShareLink.DoesNotExist:
            return Response({'detail': 'Share link not found.'}, status=status.HTTP_404_NOT_FOUND)

        if link.is_expired:
            return Response({'detail': 'This share link has expired.'}, status=status.HTTP_410_GONE)

        action_type = request.data.get('action')  # favorite, download
        if action_type == 'favorite' and link.allow_favorites and link.album:
            file_id = request.data.get('file_id')
            try:
                asset = AlbumAsset.objects.get(album=link.album, file_asset_id=file_id)
                asset.is_favorite = not asset.is_favorite
                asset.save(update_fields=['is_favorite'])
                return Response({'success': True, 'is_favorite': asset.is_favorite})
            except AlbumAsset.DoesNotExist:
                return Response({'detail': 'Asset not found in album.'}, status=status.HTTP_404_NOT_FOUND)

        elif action_type == 'download' and link.allow_downloads:
            ShareLink.objects.filter(id=link.id).update(download_count=F('download_count') + 1)
            return Response({'success': True})

        return Response({'detail': 'Action not permitted.'}, status=status.HTTP_400_BAD_REQUEST)
