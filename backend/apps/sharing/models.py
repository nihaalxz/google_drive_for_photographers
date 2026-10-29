import uuid
import secrets
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from apps.workspaces.models import Workspace
from apps.albums.models import Album
from apps.folders.models import Folder
from apps.files.models import FileAsset

class ShareTargetType(models.TextChoices):
    ALBUM = 'ALBUM', 'Album'
    FOLDER = 'FOLDER', 'Folder'
    FILE = 'FILE', 'File'

def generate_share_token():
    return secrets.token_urlsafe(24)

class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='share_links')
    token = models.CharField(max_length=64, unique=True, default=generate_share_token)
    title = models.CharField(max_length=255, blank=True)
    target_type = models.CharField(max_length=20, choices=ShareTargetType.choices)
    
    # Optional target foreign keys
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name='share_links')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='share_links')
    file_asset = models.ForeignKey(FileAsset, on_delete=models.CASCADE, null=True, blank=True, related_name='share_links')
    
    # Access controls
    password_hash = models.CharField(max_length=255, blank=True, default='')
    expires_at = models.DateTimeField(null=True, blank=True)
    allow_downloads = models.BooleanField(default=True)
    allow_favorites = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    # Metrics
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['token', 'is_active']),
            models.Index(fields=['workspace', 'is_active']),
        ]

    def __str__(self):
        return f"ShareLink: {self.token} ({self.target_type})"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_password_protected(self):
        return bool(self.password_hash)

    def set_password(self, raw_password):
        if raw_password:
            self.password_hash = make_password(raw_password)
        else:
            self.password_hash = ''

    def verify_password(self, raw_password):
        if not self.password_hash:
            return True
        return check_password(raw_password, self.password_hash)
