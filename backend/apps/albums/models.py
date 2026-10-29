import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace
from apps.files.models import FileAsset

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=255, blank=True)
    client_email = models.EmailField(blank=True)
    event_date = models.DateField(null=True, blank=True)
    cover_asset = models.ForeignKey(FileAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_albums')
    is_starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'is_deleted']),
        ]

    def __str__(self):
        return self.title

    @property
    def photo_count(self):
        return self.album_assets.count()


class AlbumAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album_assets')
    file_asset = models.ForeignKey(FileAsset, on_delete=models.CASCADE, related_name='album_memberships')
    sort_order = models.IntegerField(default=0)
    is_favorite = models.BooleanField(default=False)
    client_selected = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('album', 'file_asset')
        ordering = ['sort_order', '-added_at']

    def __str__(self):
        return f"{self.album.title} - {self.file_asset.safe_display_name}"
