import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace

class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    action = models.CharField(max_length=64)  # UPLOAD, DELETE, RESTORE, CREATE_FOLDER, SHARE, DOWNLOAD, etc.
    target_type = models.CharField(max_length=32)  # FILE, FOLDER, ALBUM, SHARE
    target_id = models.CharField(max_length=64, blank=True, default='')
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at}] {self.action}: {self.description}"
