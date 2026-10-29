import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace
from apps.folders.models import Folder

class UploadStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    UPLOADED = 'UPLOADED', 'Uploaded'
    FAILED = 'FAILED', 'Failed'

class FileAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='files')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    original_filename = models.CharField(max_length=255)
    safe_display_name = models.CharField(max_length=255)
    object_key = models.CharField(max_length=1024, unique=True)
    thumbnail_key = models.CharField(max_length=1024, blank=True, default='')
    mime_type = models.CharField(max_length=128, default='application/octet-stream')
    file_size = models.BigIntegerField(default=0)
    file_extension = models.CharField(max_length=32, blank=True)
    etag = models.CharField(max_length=128, blank=True, default='')
    upload_status = models.CharField(max_length=20, choices=UploadStatus.choices, default=UploadStatus.PENDING)
    
    # Metadata & EXIF
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    camera_make = models.CharField(max_length=128, blank=True, default='')
    camera_model = models.CharField(max_length=128, blank=True, default='')
    lens_model = models.CharField(max_length=255, blank=True, default='')
    iso = models.IntegerField(null=True, blank=True)
    f_stop = models.CharField(max_length=32, blank=True, default='')
    shutter_speed = models.CharField(max_length=32, blank=True, default='')
    focal_length = models.CharField(max_length=32, blank=True, default='')
    date_taken = models.DateTimeField(null=True, blank=True)
    raw_metadata = models.JSONField(default=dict, blank=True)

    # Status flags
    is_starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'folder', 'is_deleted']),
            models.Index(fields=['workspace', 'is_deleted', 'upload_status']),
            models.Index(fields=['workspace', 'is_deleted', 'is_starred']),
            models.Index(fields=['workspace', 'is_deleted', '-created_at']),
            models.Index(fields=['mime_type']),
        ]

    def __str__(self):
        return self.safe_display_name or self.original_filename

    @property
    def is_image(self):
        return self.mime_type.startswith('image/')

    @property
    def is_video(self):
        return self.mime_type.startswith('video/')

    @property
    def is_raw(self):
        raw_exts = {'cr2', 'cr3', 'nef', 'arw', 'dng', 'raf', 'rw2', 'orf'}
        return self.file_extension.lower() in raw_exts
