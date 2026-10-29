import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class B2StorageService:
    def __init__(self):
        self.endpoint = settings.B2_S3_ENDPOINT
        self.region = settings.B2_REGION
        self.bucket_name = settings.B2_BUCKET_NAME
        self.key_id = settings.B2_KEY_ID
        self.application_key = settings.B2_APPLICATION_KEY
        self.local_fallback = settings.B2_LOCAL_FALLBACK
        self.has_credentials = bool(self.key_id and self.application_key)

    def _get_client(self):
        if not self.has_credentials:
            return None
        return boto3.client(
            's3',
            endpoint_url=self.endpoint,
            region_name=self.region,
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.application_key,
            config=Config(signature_version='s3v4')
        )

    def generate_presigned_put(self, object_key: str, mime_type: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned PUT URL for direct browser-to-B2 upload.
        """
        if self.has_credentials:
            client = self._get_client()
            return client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'ContentType': mime_type
                },
                ExpiresIn=expires_in,
                HttpMethod='PUT'
            )
        # Local development / fallback simulation endpoint
        return f"/api/v1/storage/mock-upload/{object_key}"

    def generate_presigned_get(self, object_key: str, filename: str = None, expires_in: int = 3600) -> str:
        """
        Generate a secure presigned GET URL for downloading or previewing private objects.
        """
        if self.has_credentials:
            client = self._get_client()
            params = {
                'Bucket': self.bucket_name,
                'Key': object_key,
            }
            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
            return client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
        # Local development / fallback
        if filename:
            return f"/api/v1/storage/mock-download/{object_key}?filename={filename}"
        return f"/api/v1/storage/mock-download/{object_key}"

    def create_multipart_upload(self, object_key: str, mime_type: str) -> str:
        """
        Initiate an S3 multipart upload for large files (>100MB).
        """
        if self.has_credentials:
            client = self._get_client()
            res = client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_key,
                ContentType=mime_type
            )
            return res['UploadId']
        return "mock-upload-id-multipart"

    def generate_presigned_part_url(self, object_key: str, upload_id: str, part_number: int, expires_in: int = 3600) -> str:
        """
        Generate presigned URL for a specific multipart part.
        """
        if self.has_credentials:
            client = self._get_client()
            return client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'UploadId': upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=expires_in,
                HttpMethod='PUT'
            )
        return f"/api/v1/storage/mock-upload-part/{object_key}?uploadId={upload_id}&partNumber={part_number}"

    def complete_multipart_upload(self, object_key: str, upload_id: str, parts: list):
        """
        Complete S3 multipart upload by providing list of parts with PartNumber and ETag.
        """
        if self.has_credentials:
            client = self._get_client()
            return client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
        return {'ETag': 'mock-etag-complete'}

    def abort_multipart_upload(self, object_key: str, upload_id: str):
        """
        Abort an abandoned multipart upload session to prevent orphaned storage charges.
        """
        if self.has_credentials:
            client = self._get_client()
            return client.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_key,
                UploadId=upload_id
            )
        return True

    def verify_object(self, object_key: str) -> dict:
        """
        Verify object existence, size, and etag directly in Backblaze B2.
        """
        if self.has_credentials:
            client = self._get_client()
            try:
                res = client.head_object(Bucket=self.bucket_name, Key=object_key)
                return {
                    'exists': True,
                    'size': res.get('ContentLength', 0),
                    'etag': res.get('ETag', '').strip('"'),
                    'content_type': res.get('ContentType', '')
                }
            except ClientError as e:
                logger.warning(f"Error checking object {object_key}: {e}")
                return {'exists': False, 'size': 0, 'etag': '', 'content_type': ''}
        # In fallback mode, check if file exists in media mock storage
        mock_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
        if os.path.exists(mock_path):
            size = os.path.getsize(mock_path)
            return {'exists': True, 'size': size, 'etag': 'mock-local-etag', 'content_type': 'application/octet-stream'}
        # Default mock fallback for simulated uploads
        return {'exists': True, 'size': 1024, 'etag': 'mock-local-etag', 'content_type': 'image/jpeg'}

    def upload_bytes(self, object_key: str, data: bytes, content_type: str = 'image/webp') -> bool:
        """
        Directly upload in-memory bytes (e.g. compressed WebP thumbnails) to Backblaze B2
        with immutable long-lived HTTP caching headers.
        """
        if self.has_credentials:
            client = self._get_client()
            client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=data,
                ContentType=content_type,
                CacheControl='public, max-age=31536000, immutable'
            )
            return True
        else:
            mock_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
            os.makedirs(os.path.dirname(mock_path), exist_ok=True)
            with open(mock_path, 'wb') as f:
                f.write(data)
            return True

    def get_object_bytes(self, object_key: str) -> bytes:
        """
        Retrieve object raw bytes from Backblaze B2 or local mock storage.
        """
        if self.has_credentials:
            client = self._get_client()
            try:
                response = client.get_object(Bucket=self.bucket_name, Key=object_key)
                return response['Body'].read()
            except Exception as e:
                logger.error(f"Error reading object bytes for {object_key}: {e}")
                return b''
        else:
            mock_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
            if os.path.exists(mock_path):
                with open(mock_path, 'rb') as f:
                    return f.read()
            return b''

    def delete_object(self, object_key: str):
        """
        Delete object from storage bucket.
        """
        if self.has_credentials:
            client = self._get_client()
            client.delete_object(Bucket=self.bucket_name, Key=object_key)
        else:
            mock_path = os.path.join(settings.MEDIA_ROOT, 'mock_storage', object_key)
            if os.path.exists(mock_path):
                try:
                    os.remove(mock_path)
                except OSError:
                    pass

b2_service = B2StorageService()

