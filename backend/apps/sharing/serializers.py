from rest_framework import serializers
from .models import ShareLink
from apps.albums.serializers import AlbumSerializer
from apps.folders.serializers import FolderSerializer
from apps.files.serializers import FileAssetSerializer

class ShareLinkSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    is_password_protected = serializers.ReadOnlyField()
    album_title = serializers.CharField(source='album.title', read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    file_name = serializers.CharField(source='file_asset.safe_display_name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ShareLink
        fields = [
            'id', 'workspace', 'token', 'title', 'target_type',
            'album', 'folder', 'file_asset', 'album_title', 'folder_name', 'file_name',
            'is_password_protected', 'expires_at', 'is_expired',
            'allow_downloads', 'allow_favorites', 'is_active',
            'view_count', 'download_count', 'created_at', 'updated_at', 'password'
        ]
        read_only_fields = ['id', 'token', 'workspace', 'view_count', 'download_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = ShareLink(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
