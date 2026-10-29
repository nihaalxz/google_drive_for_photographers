from rest_framework import serializers
from .models import Album, AlbumAsset
from apps.files.serializers import FileAssetSerializer

class AlbumAssetSerializer(serializers.ModelSerializer):
    file_asset = FileAssetSerializer(read_only=True)

    class Meta:
        model = AlbumAsset
        fields = ['id', 'album', 'file_asset', 'sort_order', 'is_favorite', 'client_selected', 'added_at']

class AlbumSerializer(serializers.ModelSerializer):
    photo_count = serializers.ReadOnlyField()
    cover_asset = FileAssetSerializer(read_only=True)
    cover_asset_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Album
        fields = [
            'id', 'workspace', 'title', 'description', 'client_name', 'client_email',
            'event_date', 'cover_asset', 'cover_asset_id', 'photo_count', 'is_starred',
            'is_deleted', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'workspace', 'created_by', 'created_at', 'updated_at', 'photo_count']
