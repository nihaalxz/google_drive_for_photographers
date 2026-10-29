from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import FileAsset, UploadStatus
from .serializers import FileAssetSerializer
from apps.folders.models import Folder
from apps.storage.services.b2 import b2_service
from apps.activity.models import ActivityLog

class FileAssetViewSet(viewsets.ModelViewSet):
    serializer_class = FileAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = FileAsset.objects.filter(workspace__memberships__user=user)

        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        # Trash filter
        if self.action in ['restore', 'permanent_delete']:
            pass
        else:
            show_deleted = self.request.query_params.get('deleted', 'false').lower() == 'true'
            qs = qs.filter(is_deleted=show_deleted)

        # Starred filter
        is_starred = self.request.query_params.get('starred')
        if is_starred:
            qs = qs.filter(is_starred=(is_starred.lower() == 'true'))

        # Folder filter
        folder_id = self.request.query_params.get('folder_id')
        if folder_id == 'root' or folder_id == 'null':
            qs = qs.filter(folder__isnull=True)
        elif folder_id:
            qs = qs.filter(folder_id=folder_id)

        # File type filter
        file_type = self.request.query_params.get('type')
        if file_type == 'image':
            qs = qs.filter(mime_type__startswith='image/')
        elif file_type == 'video':
            qs = qs.filter(mime_type__startswith='video/')
        elif file_type == 'raw':
            raw_exts = ['cr2', 'cr3', 'nef', 'arw', 'dng', 'raf', 'rw2', 'orf']
            qs = qs.filter(file_extension__in=raw_exts)

        # Search query
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(safe_display_name__icontains=q) |
                Q(original_filename__icontains=q) |
                Q(camera_make__icontains=q) |
                Q(camera_model__icontains=q) |
                Q(lens_model__icontains=q)
            )

        # Sorting
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        sort_dir = self.request.query_params.get('sort_direction', 'desc')
        field_map = {
            'name': 'safe_display_name',
            'size': 'file_size',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'type': 'mime_type',
        }
        order_field = field_map.get(sort_by, 'created_at')
        if sort_dir == 'desc':
            order_field = f"-{order_field}"

        return qs.order_by(order_field)

    def perform_destroy(self, instance):
        # Soft delete (move to trash)
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

        ActivityLog.objects.create(
            workspace=instance.workspace,
            user=self.request.user,
            action='TRASH_FILE',
            target_type='FILE',
            target_id=str(instance.id),
            description=f"Moved '{instance.safe_display_name}' to trash"
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        file_asset = self.get_object()
        file_asset.is_deleted = False
        file_asset.deleted_at = None
        file_asset.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

        ActivityLog.objects.create(
            workspace=file_asset.workspace,
            user=request.user,
            action='RESTORE_FILE',
            target_type='FILE',
            target_id=str(file_asset.id),
            description=f"Restored '{file_asset.safe_display_name}' from trash"
        )
        return Response(FileAssetSerializer(file_asset).data)

    @action(detail=True, methods=['post'])
    def toggle_star(self, request, pk=None):
        file_asset = self.get_object()
        file_asset.is_starred = not file_asset.is_starred
        file_asset.save(update_fields=['is_starred', 'updated_at'])
        return Response({'is_starred': file_asset.is_starred})

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        file_asset = self.get_object()
        new_folder_id = request.data.get('folder_id')
        if new_folder_id:
            folder = Folder.objects.get(id=new_folder_id, workspace=file_asset.workspace)
            file_asset.folder = folder
        else:
            file_asset.folder = None
        file_asset.save(update_fields=['folder', 'updated_at'])
        return Response(FileAssetSerializer(file_asset).data)

    @action(detail=True, methods=['delete'])
    def permanent_delete(self, request, pk=None):
        file_asset = self.get_object()
        workspace = file_asset.workspace
        size = file_asset.file_size
        object_key = file_asset.object_key

        # Delete from Backblaze B2 object storage
        try:
            b2_service.delete_object(object_key)
        except Exception as e:
            pass

        # Update storage quota ledger
        workspace.storage_used_bytes = max(0, workspace.storage_used_bytes - size)
        workspace.save(update_fields=['storage_used_bytes', 'updated_at'])

        ActivityLog.objects.create(
            workspace=workspace,
            user=request.user,
            action='PERMANENT_DELETE_FILE',
            target_type='FILE',
            target_id=str(file_asset.id),
            description=f"Permanently deleted '{file_asset.safe_display_name}' ({size} bytes)"
        )

        file_asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        action_type = request.data.get('action')  # trash, restore, delete_permanent, star, unstar, move
        file_ids = request.data.get('file_ids', [])

        user_files = self.get_queryset().filter(id__in=file_ids)
        now = timezone.now()

        if action_type == 'trash':
            user_files.update(is_deleted=True, deleted_at=now)
        elif action_type == 'restore':
            user_files.update(is_deleted=False, deleted_at=None)
        elif action_type == 'star':
            user_files.update(is_starred=True)
        elif action_type == 'unstar':
            user_files.update(is_starred=False)
        elif action_type == 'move':
            new_folder_id = request.data.get('folder_id')
            new_folder = None
            if new_folder_id:
                new_folder = Folder.objects.filter(id=new_folder_id, workspace__memberships__user=request.user).first()
            user_files.update(folder=new_folder)
        elif action_type == 'delete_permanent':
            for f in user_files:
                try:
                    b2_service.delete_object(f.object_key)
                except Exception:
                    pass
                ws = f.workspace
                ws.storage_used_bytes = max(0, ws.storage_used_bytes - f.file_size)
                ws.save(update_fields=['storage_used_bytes', 'updated_at'])
            user_files.delete()
        else:
            return Response({'detail': f"Unsupported bulk action '{action_type}'"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'count': len(file_ids)})
