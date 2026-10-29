import os
import uuid
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

import base64
import logging
from .models import UploadSession, UploadSessionStatus
from .services.b2 import b2_service
from apps.workspaces.models import Workspace
from apps.folders.models import Folder
from apps.files.models import FileAsset, UploadStatus
from apps.files.serializers import FileAssetSerializer
from apps.files.utils import generate_compressed_thumbnail
from apps.activity.models import ActivityLog

logger = logging.getLogger(__name__)

class CreateUploadSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        workspace_id = data.get('workspace_id')
        original_filename = data.get('original_filename', '').strip()
        file_size = int(data.get('file_size', 0))
        mime_type = data.get('mime_type', 'application/octet-stream')
        folder_id = data.get('folder_id')

        if not workspace_id or not original_filename or file_size <= 0:
            return Response({'detail': 'workspace_id, original_filename, and valid file_size are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace membership
        try:
            workspace = Workspace.objects.get(id=workspace_id, memberships__user=request.user)
        except Workspace.DoesNotExist:
            return Response({'detail': 'Workspace not found or access denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Quota check
        if workspace.storage_used_bytes + file_size > workspace.storage_limit_bytes:
            return Response({
                'detail': 'Storage quota exceeded. Please upgrade your storage plan or remove old files.',
                'quota_limit': workspace.storage_limit_bytes,
                'used': workspace.storage_used_bytes,
                'required': file_size
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify folder if provided
        folder = None
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, workspace=workspace, is_deleted=False)
            except Folder.DoesNotExist:
                return Response({'detail': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate safe object key
        name_stem = Path(original_filename).stem
        ext = Path(original_filename).suffix.lstrip('.').lower()
        safe_name = f"{slugify(name_stem) or 'file'}.{ext}" if ext else (slugify(name_stem) or 'file')
        asset_uuid = uuid.uuid4()
        object_key = f"workspaces/{workspace.id}/originals/{asset_uuid}/{safe_name}"

        # Decide between single PUT vs Multipart S3 upload
        # Files > 100MB use multipart upload
        MULTIPART_THRESHOLD = 100 * 1024 * 1024  # 100MB
        PART_SIZE = 20 * 1024 * 1024  # 20MB per part

        is_multipart = file_size > MULTIPART_THRESHOLD
        upload_id = ''
        presigned_data = {}

        if is_multipart:
            part_count = (file_size + PART_SIZE - 1) // PART_SIZE
            upload_id = b2_service.create_multipart_upload(object_key, mime_type)
            part_urls = []
            for part_num in range(1, part_count + 1):
                p_url = b2_service.generate_presigned_part_url(object_key, upload_id, part_num)
                part_urls.append({'part_number': part_num, 'url': p_url})
            presigned_data = {
                'part_size': PART_SIZE,
                'part_count': part_count,
                'parts': part_urls
            }
        else:
            upload_url = b2_service.generate_presigned_put(object_key, mime_type)
            presigned_data = {
                'upload_url': upload_url
            }

        session = UploadSession.objects.create(
            workspace=workspace,
            user=request.user,
            folder=folder,
            original_filename=original_filename,
            safe_display_name=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            object_key=object_key,
            upload_id=upload_id,
            is_multipart=is_multipart,
            part_count=presigned_data.get('part_count', 1),
            part_size=presigned_data.get('part_size', file_size),
            presigned_data=presigned_data,
            expires_at=timezone.now() + timedelta(hours=3)
        )

        return Response({
            'session_id': str(session.id),
            'object_key': object_key,
            'is_multipart': is_multipart,
            'presigned_data': presigned_data,
            'expires_at': session.expires_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class CompleteUploadSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        etag = request.data.get('etag', '')
        parts = request.data.get('parts', [])  # for multipart: [{'PartNumber': 1, 'ETag': '...'}]

        try:
            session = UploadSession.objects.get(id=session_id, user=request.user)
        except UploadSession.DoesNotExist:
            return Response({'detail': 'Upload session not found.'}, status=status.HTTP_404_NOT_FOUND)

        if session.status != UploadSessionStatus.INITIATED:
            return Response({'detail': f'Session cannot be completed in {session.status} status.'}, status=status.HTTP_400_BAD_REQUEST)

        # Complete multipart if necessary
        if session.is_multipart:
            try:
                b2_service.complete_multipart_upload(session.object_key, session.upload_id, parts)
            except Exception as e:
                session.status = UploadSessionStatus.FAILED
                session.save(update_fields=['status', 'updated_at'])
                return Response({'detail': f'Failed to complete multipart upload: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify uploaded object existence & size with B2
        verification = b2_service.verify_object(session.object_key)
        if not verification.get('exists'):
            return Response({'detail': 'Uploaded object could not be verified in storage.'}, status=status.HTTP_400_BAD_REQUEST)

        actual_size = verification.get('size') or session.file_size
        actual_etag = verification.get('etag') or etag

        ext = Path(session.original_filename).suffix.lstrip('.').lower()

        # Extract optional client-provided EXIF/camera metadata
        exif_data = request.data.get('metadata', {})

        # Process thumbnail: check client base64 thumbnail first, then server fallback
        thumbnail_base64 = request.data.get('thumbnail_base64')
        thumb_key = ''
        if thumbnail_base64 and isinstance(thumbnail_base64, str):
            try:
                if ',' in thumbnail_base64:
                    _, b64data = thumbnail_base64.split(',', 1)
                else:
                    b64data = thumbnail_base64
                thumb_bytes = base64.b64decode(b64data)
                if thumb_bytes and len(thumb_bytes) < 3 * 1024 * 1024:
                    thumb_key = f"thumbnails/{session.workspace.id}/{uuid.uuid4().hex}.webp"
                    b2_service.upload_bytes(thumb_key, thumb_bytes, content_type='image/webp')
            except Exception as e:
                logger.warning(f"Could not save client uploaded thumbnail: {e}")

        # Server-side fallback for images under 15MB if client thumbnail was not supplied
        if not thumb_key and session.mime_type.startswith('image/') and actual_size < 15 * 1024 * 1024:
            try:
                raw_bytes = b2_service.get_object_bytes(session.object_key)
                if raw_bytes:
                    thumb_bytes = generate_compressed_thumbnail(raw_bytes)
                    if thumb_bytes:
                        thumb_key = f"thumbnails/{session.workspace.id}/{uuid.uuid4().hex}.webp"
                        b2_service.upload_bytes(thumb_key, thumb_bytes, content_type='image/webp')
            except Exception as e:
                logger.warning(f"Could not auto-generate thumbnail on completeSession: {e}")

        file_asset = FileAsset.objects.create(
            workspace=session.workspace,
            folder=session.folder,
            original_filename=session.original_filename,
            safe_display_name=session.safe_display_name,
            object_key=session.object_key,
            thumbnail_key=thumb_key,
            mime_type=session.mime_type,
            file_size=actual_size,
            file_extension=ext,
            etag=actual_etag,
            upload_status=UploadStatus.UPLOADED,
            width=exif_data.get('width'),
            height=exif_data.get('height'),
            camera_make=exif_data.get('camera_make', ''),
            camera_model=exif_data.get('camera_model', ''),
            lens_model=exif_data.get('lens_model', ''),
            iso=exif_data.get('iso'),
            f_stop=exif_data.get('f_stop', ''),
            shutter_speed=exif_data.get('shutter_speed', ''),
            focal_length=exif_data.get('focal_length', ''),
            date_taken=exif_data.get('date_taken'),
            raw_metadata=exif_data.get('raw', {}),
            uploaded_by=request.user
        )

        # Update authoritative storage ledger
        workspace = session.workspace
        workspace.storage_used_bytes += actual_size
        workspace.save(update_fields=['storage_used_bytes', 'updated_at'])

        # Mark session complete
        session.status = UploadSessionStatus.COMPLETED
        session.save(update_fields=['status', 'updated_at'])

        ActivityLog.objects.create(
            workspace=workspace,
            user=request.user,
            action='UPLOAD_FILE',
            target_type='FILE',
            target_id=str(file_asset.id),
            description=f"Uploaded '{file_asset.safe_display_name}' ({actual_size} bytes)"
        )

        return Response(FileAssetSerializer(file_asset).data, status=status.HTTP_201_CREATED)


class AbortUploadSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        try:
            session = UploadSession.objects.get(id=session_id, user=request.user)
        except UploadSession.DoesNotExist:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

        if session.is_multipart and session.upload_id:
            b2_service.abort_multipart_upload(session.object_key, session.upload_id)

        session.status = UploadSessionStatus.ABORTED
        session.save(update_fields=['status', 'updated_at'])
        return Response({'success': True})


class MockUploadHandlerView(APIView):
    """
    Fallback endpoint for local testing and dev when Backblaze B2 credentials are empty.
    Simulates direct PUT upload into media/mock_storage.
    """
    permission_classes = [permissions.AllowAny]

    def put(self, request, object_key):
        save_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(request.body)
        response = HttpResponse(status=200)
        response['ETag'] = '"mock-etag-local"'
        return response


class MockDownloadHandlerView(APIView):
    """
    Fallback endpoint to serve uploaded mock files in local development.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, object_key):
        file_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
        if os.path.exists(file_path):
            filename = request.query_params.get('filename')
            response = FileResponse(open(file_path, 'rb'))
            if filename:
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        # Return fallback placeholder SVG if not on disk
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
            <rect width="800" height="600" fill="#18181b"/>
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#71717a" font-family="sans-serif" font-size="20">
                LensVault Preview ({object_key.split('/')[-1]})
            </text>
        </svg>'''
        return HttpResponse(svg_content, content_type='image/svg+xml')
