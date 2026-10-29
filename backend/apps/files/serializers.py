from rest_framework import serializers
from .models import FileAsset
from apps.storage.services.b2 import b2_service

class FileAssetSerializer(serializers.ModelSerializer):
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
            'preview_url', 'download_url', 'is_image', 'is_video', 'is_raw'
        ]
        read_only_fields = [
            'id', 'workspace', 'original_filename', 'mime_type', 'file_size',
            'file_extension', 'etag', 'upload_status', 'width', 'height',
            'camera_make', 'camera_model', 'lens_model', 'iso', 'f_stop',
            'shutter_speed', 'focal_length', 'date_taken', 'raw_metadata',
            'is_deleted', 'deleted_at', 'uploaded_by', 'created_at', 'updated_at'
        ]

    def get_preview_url(self, obj):
        if obj.upload_status != 'UPLOADED':
            return None
        # Return secure signed URL
        return b2_service.generate_presigned_get(obj.object_key, filename=None, expires_in=7200)

    def get_download_url(self, obj):
        if obj.upload_status != 'UPLOADED':
            return None
        return b2_service.generate_presigned_get(obj.object_key, filename=obj.safe_display_name, expires_in=3600)
