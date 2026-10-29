import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace
from apps.folders.models import Folder

class UploadSessionStatus(models.TextChoices):
    INITIATED = 'INITIATED', 'Initiated'
    COMPLETED = 'COMPLETED', 'Completed'
    ABORTED = 'ABORTED', 'Aborted'
    EXPIRED = 'EXPIRED', 'Expired'

class UploadSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='upload_sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='upload_sessions')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True)
    original_filename = models.CharField(max_length=255)
    safe_display_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=128)
    object_key = models.CharField(max_length=1024)
    upload_id = models.CharField(max_length=255, blank=True, default='')  # S3 Multipart Upload ID
    is_multipart = models.BooleanField(default=False)
    part_count = models.IntegerField(default=1)
    part_size = models.BigIntegerField(default=0)
    presigned_data = models.JSONField(default=dict, blank=True)  # Stores presigned URLs / part URLs
    status = models.CharField(max_length=20, choices=UploadSessionStatus.choices, default=UploadSessionStatus.INITIATED)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['object_key']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.status})"
