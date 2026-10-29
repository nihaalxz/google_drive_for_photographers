from rest_framework import serializers
from .models import Folder

class FolderSerializer(serializers.ModelSerializer):
    breadcrumbs = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = [
            'id', 'workspace', 'parent', 'name', 'color', 'is_starred',
            'is_deleted', 'deleted_at', 'created_by', 'created_at', 'updated_at',
            'breadcrumbs', 'children_count', 'files_count'
        ]
        read_only_fields = ['id', 'workspace', 'created_by', 'created_at', 'updated_at', 'breadcrumbs', 'children_count', 'files_count']

    def get_breadcrumbs(self, obj):
        return obj.get_breadcrumbs()

    def get_children_count(self, obj):
        return obj.children.filter(is_deleted=False).count()

    def get_files_count(self, obj):
        return obj.files.filter(is_deleted=False).count()

class FolderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'parent', 'name', 'color']

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Folder name cannot be empty.")
        if '/' in trimmed or '\\' in trimmed:
            raise serializers.ValidationError("Folder name cannot contain slashes.")
        return trimmed
