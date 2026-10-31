from rest_framework import serializers
from .models import FileAsset
from apps.storage.services.b2 import b2_service

from django.conf import settings

class FileAssetSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_raw = serializers.ReadOnlyField()

    class Meta:
        model = FileAsset
        fields = [
            'id', 'workspace', 'folder', 'original_filename', 'safe_display_name',
            'mime_type', 'file_size', 'file_extension', 'etag', 'upload_status',
            'width', 'height', 'camera_make', 'camera_model', 'lens_model',
            'iso', 'f_stop', 'shutter_speed', 'focal_length', 'date_taken',
            'raw_metadata', 'is_starred', 'is_deleted', 'deleted_at',
            'uploaded_by', 'created_at', 'updated_at',
            'thumbnail_url', 'preview_url', 'download_url', 'is_image', 'is_video', 'is_raw'
        ]
        read_only_fields = [
            'id', 'workspace', 'original_filename', 'mime_type', 'file_size',
            'file_extension', 'etag', 'upload_status', 'width', 'height',
            'camera_make', 'camera_model', 'lens_model', 'iso', 'f_stop',
            'shutter_speed', 'focal_length', 'date_taken', 'raw_metadata',
            'is_deleted', 'deleted_at', 'uploaded_by', 'created_at', 'updated_at'
        ]

    def _ensure_absolute_url(self, url: str) -> str:
        if not url:
            return url
        if not url.startswith('http'):
            request = self.context.get('request')
            if request:
                url = request.build_absolute_uri(url)
        # Prevent Mixed Content blocking in browsers
        if url.startswith('http://'):
            request = self.context.get('request')
            is_https = (request and (request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO') == 'https')) or not settings.DEBUG
            if is_https:
                url = 'https://' + url[7:]
        return url

    def get_thumbnail_url(self, obj):
        if obj.upload_status != 'UPLOADED':
            return None
        # Always route image thumbnails and existing video thumbnails through the proxy endpoint.
        # This streams the cached WebP thumbnail (or on-the-fly generates it),
        # ensuring 100% reliable rendering without 403 Forbidden or CORS issues.
        if obj.is_image or (obj.is_video and obj.thumbnail_key):
            raw_url = f"/api/v1/files/{obj.id}/thumbnail/"
            return self._ensure_absolute_url(raw_url)
        return None

    def get_preview_url(self, obj):
        if obj.upload_status != 'UPLOADED':
            return None
        # For images, route through preview endpoint for direct backend streaming
        if obj.is_image:
            raw_url = f"/api/v1/files/{obj.id}/preview/"
            return self._ensure_absolute_url(raw_url)
        # Return secure signed URL for video/other files
        url = b2_service.generate_presigned_get(obj.object_key, filename=None, expires_in=7200)
        return self._ensure_absolute_url(url)

    def get_download_url(self, obj):
        if obj.upload_status != 'UPLOADED':
            return None
        url = b2_service.generate_presigned_get(obj.object_key, filename=obj.safe_display_name, expires_in=3600)
        return self._ensure_absolute_url(url)

