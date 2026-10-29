from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Folder
from .serializers import FolderSerializer, FolderCreateSerializer
from apps.workspaces.models import Workspace
from apps.activity.models import ActivityLog

class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Folder.objects.filter(workspace__memberships__user=user)
        
        # Workspace filter
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        # Deleted status
        if self.action in ['restore']:
            pass
        else:
            show_deleted = self.request.query_params.get('deleted', 'false').lower() == 'true'
            qs = qs.filter(is_deleted=show_deleted)

        # Starred filter
        is_starred = self.request.query_params.get('starred')
        if is_starred:
            qs = qs.filter(is_starred=(is_starred.lower() == 'true'))

        # Parent folder filter
        parent_id = self.request.query_params.get('parent_id')
        if parent_id == 'root' or parent_id == 'null':
            qs = qs.filter(parent__isnull=True)
        elif parent_id:
            qs = qs.filter(parent_id=parent_id)

        # Search
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q)

        return qs.select_related('workspace', 'parent').prefetch_related('children', 'files')

    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = Workspace.objects.get(id=workspace_id, memberships__user=self.request.user)
        folder = serializer.save(
            workspace=workspace,
            created_by=self.request.user
        )
        ActivityLog.objects.create(
            workspace=workspace,
            user=self.request.user,
            action='CREATE_FOLDER',
            target_type='FOLDER',
            target_id=str(folder.id),
            description=f"Created folder '{folder.name}'"
        )

    def perform_destroy(self, instance):
        # Soft delete folder and descendant files & folders
        now = timezone.now()
        descendant_ids = instance.get_all_descendant_ids()
        
        Folder.objects.filter(id__in=descendant_ids).update(is_deleted=True, deleted_at=now)
        instance.workspace.files.filter(folder_id__in=descendant_ids).update(is_deleted=True, deleted_at=now)
        
        ActivityLog.objects.create(
            workspace=instance.workspace,
            user=self.request.user,
            action='TRASH_FOLDER',
            target_type='FOLDER',
            target_id=str(instance.id),
            description=f"Moved folder '{instance.name}' to trash"
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        folder = self.get_object()
        descendant_ids = folder.get_all_descendant_ids()
        Folder.objects.filter(id__in=descendant_ids).update(is_deleted=False, deleted_at=None)
        folder.workspace.files.filter(folder_id__in=descendant_ids).update(is_deleted=False, deleted_at=None)
        
        ActivityLog.objects.create(
            workspace=folder.workspace,
            user=request.user,
            action='RESTORE_FOLDER',
            target_type='FOLDER',
            target_id=str(folder.id),
            description=f"Restored folder '{folder.name}'"
        )
        return Response(FolderSerializer(folder).data)

    @action(detail=True, methods=['post'])
    def toggle_star(self, request, pk=None):
        folder = self.get_object()
        folder.is_starred = not folder.is_starred
        folder.save(update_fields=['is_starred', 'updated_at'])
        return Response({'is_starred': folder.is_starred})

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        folder = self.get_object()
        new_parent_id = request.data.get('parent_id')

        if new_parent_id:
            # Cannot move into itself or any descendant
            descendant_ids = [str(fid) for fid in folder.get_all_descendant_ids()]
            if str(new_parent_id) in descendant_ids:
                return Response({'detail': 'Cannot move folder inside itself or its subfolders.'}, status=status.HTTP_400_BAD_REQUEST)
            new_parent = Folder.objects.get(id=new_parent_id, workspace=folder.workspace)
            folder.parent = new_parent
        else:
            folder.parent = None

        folder.save(update_fields=['parent', 'updated_at'])
        return Response(FolderSerializer(folder).data)
