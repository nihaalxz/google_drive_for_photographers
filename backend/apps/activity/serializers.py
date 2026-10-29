from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'workspace', 'user', 'user_email', 'action', 'target_type', 'target_id', 'description', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']
