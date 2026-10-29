from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Album, AlbumAsset
from .serializers import AlbumSerializer, AlbumAssetSerializer
from apps.workspaces.models import Workspace
from apps.files.models import FileAsset
from apps.activity.models import ActivityLog

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Album.objects.filter(workspace__memberships__user=user, is_deleted=False)

        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        starred = self.request.query_params.get('starred')
        if starred:
            qs = qs.filter(is_starred=(starred.lower() == 'true'))

        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q)

        return qs.select_related('workspace', 'cover_asset')

    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = Workspace.objects.get(id=workspace_id, memberships__user=self.request.user)
        cover_id = self.request.data.get('cover_asset_id')
        cover = None
        if cover_id:
            cover = FileAsset.objects.filter(id=cover_id, workspace=workspace).first()

        album = serializer.save(
            workspace=workspace,
            cover_asset=cover,
            created_by=self.request.user
        )

        ActivityLog.objects.create(
            workspace=workspace,
            user=self.request.user,
            action='CREATE_ALBUM',
            target_type='ALBUM',
            target_id=str(album.id),
            description=f"Created client album '{album.title}'"
        )

    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        album = self.get_object()
        assets = AlbumAsset.objects.filter(album=album).select_related('file_asset')
        return Response(AlbumAssetSerializer(assets, many=True).data)

    @action(detail=True, methods=['post'])
    def add_assets(self, request, pk=None):
        album = self.get_object()
        file_ids = request.data.get('file_ids', [])
        
        files = FileAsset.objects.filter(
            id__in=file_ids,
            workspace=album.workspace,
            is_deleted=False
        )
        
        added_count = 0
        for f in files:
            _, created = AlbumAsset.objects.get_or_create(album=album, file_asset=f)
            if created:
                added_count += 1
                if not album.cover_asset:
                    album.cover_asset = f
                    album.save(update_fields=['cover_asset', 'updated_at'])

        return Response({'success': True, 'added': added_count, 'photo_count': album.photo_count})

    @action(detail=True, methods=['post'])
    def remove_asset(self, request, pk=None):
        album = self.get_object()
        file_id = request.data.get('file_id')
        AlbumAsset.objects.filter(album=album, file_asset_id=file_id).delete()
        if album.cover_asset_id == file_id:
            next_asset = AlbumAsset.objects.filter(album=album).first()
            album.cover_asset = next_asset.file_asset if next_asset else None
            album.save(update_fields=['cover_asset', 'updated_at'])
        return Response({'success': True, 'photo_count': album.photo_count})

    @action(detail=True, methods=['post'])
    def set_cover(self, request, pk=None):
        album = self.get_object()
        file_id = request.data.get('file_id')
        file_asset = FileAsset.objects.get(id=file_id, workspace=album.workspace)
        album.cover_asset = file_asset
        album.save(update_fields=['cover_asset', 'updated_at'])
        return Response(AlbumSerializer(album).data)

    @action(detail=True, methods=['post'])
    def toggle_star(self, request, pk=None):
        album = self.get_object()
        album.is_starred = not album.is_starred
        album.save(update_fields=['is_starred', 'updated_at'])
        return Response({'is_starred': album.is_starred})
