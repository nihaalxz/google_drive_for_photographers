import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace

class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=32, blank=True, default='')
    is_starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['workspace', 'parent', 'is_deleted']),
            models.Index(fields=['workspace', 'is_deleted', 'is_starred']),
            models.Index(fields=['workspace', 'is_deleted', 'updated_at']),
        ]

    def __str__(self):
        return self.name

    def get_breadcrumbs(self):
        crumbs = []
        curr = self
        while curr:
            crumbs.append({'id': str(curr.id), 'name': curr.name})
            curr = curr.parent
        return list(reversed(crumbs))

    def get_all_descendant_ids(self):
        ids = [self.id]
        children = Folder.objects.filter(parent=self)
        for child in children:
            ids.extend(child.get_all_descendant_ids())
        return ids
