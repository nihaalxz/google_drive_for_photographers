from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Workspace, WorkspaceMembership, WorkspaceRole
from .serializers import WorkspaceSerializer, WorkspaceMembershipSerializer
from apps.files.models import FileAsset

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Isolation: user can only see workspaces they are a member of
        return Workspace.objects.filter(memberships__user=self.request.user).distinct()

    @action(detail=True, methods=['get'])
    def storage_breakdown(self, request, pk=None):
        workspace = self.get_object()
        active_files = FileAsset.objects.filter(workspace=workspace, is_deleted=False)

        raw_exts = ['cr2', 'cr3', 'nef', 'arw', 'dng', 'raf', 'rw2', 'orf']
        raw_size = active_files.filter(file_extension__in=raw_exts).aggregate(s=Sum('file_size'))['s'] or 0
        image_size = active_files.filter(mime_type__startswith='image/').exclude(file_extension__in=raw_exts).aggregate(s=Sum('file_size'))['s'] or 0
        video_size = active_files.filter(mime_type__startswith='video/').aggregate(s=Sum('file_size'))['s'] or 0
        other_size = max(0, workspace.storage_used_bytes - (raw_size + image_size + video_size))

        return Response({
            'total_limit_bytes': workspace.storage_limit_bytes,
            'used_bytes': workspace.storage_used_bytes,
            'available_bytes': workspace.storage_available_bytes,
            'used_percent': workspace.storage_used_percent,
            'breakdown': {
                'raw_bytes': raw_size,
                'standard_images_bytes': image_size,
                'videos_bytes': video_size,
                'other_bytes': other_size,
            },
            'file_count': active_files.count()
        })

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        workspace = self.get_object()
        if request.method == 'GET':
            members = WorkspaceMembership.objects.filter(workspace=workspace).select_related('user')
            return Response(WorkspaceMembershipSerializer(members, many=True).data)

        # POST: add member
        # Verify requesting user is OWNER or ADMIN
        curr_mem = WorkspaceMembership.objects.filter(workspace=workspace, user=request.user).first()
        if not curr_mem or curr_mem.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            return Response({'detail': 'Only workspace owners or admins can invite members.'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', WorkspaceRole.MEMBER)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            target_user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email not found.'}, status=status.HTTP_404_NOT_FOUND)

        membership, created = WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=target_user,
            defaults={'role': role}
        )
        if not created:
            membership.role = role
            membership.save()

        return Response(WorkspaceMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)
