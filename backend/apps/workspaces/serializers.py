from rest_framework import serializers
from .models import Workspace, WorkspaceMembership
from apps.accounts.serializers import UserSerializer

class WorkspaceSerializer(serializers.ModelSerializer):
    storage_available_bytes = serializers.ReadOnlyField()
    storage_used_percent = serializers.ReadOnlyField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'storage_limit_bytes', 'storage_used_bytes',
            'storage_available_bytes', 'storage_used_percent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'storage_used_bytes', 'created_at', 'updated_at']

class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ['id', 'workspace', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']
