# Backblaze B2 Integration Guide

LensVault integrates with Backblaze B2 via its S3-compatible API to store uncompressed photography master files, RAW digital negatives, and preview derivatives.

## Architecture Highlights

1. **Private Bucket Security**:
   - The bucket `B2_BUCKET_NAME` is strictly private (`allPrivate`). Public access is blocked.
   - Files are never accessed via public URLs. All downloads and previews use short-lived AWS SigV4 presigned URLs generated on demand by Django.

2. **Direct-to-B2 Upload Flow**:
   - Web browser requests an authorized upload session from `POST /api/v1/storage/upload-session/`.
   - Django validates user quota, file type, and workspace membership.
   - Django signs an S3 Presigned PUT URL (for files <= 100MB) or an S3 Multipart Upload Session (for large files > 100MB).
   - The client browser streams bytes directly to Backblaze B2's S3 endpoint with progress feedback.
   - The client informs Django via `POST /api/v1/storage/upload-complete/`.
   - Django validates the object in B2 using `head_object` and records authoritative metadata and storage accounting in MySQL.

3. **Multipart Strategy**:
   - Files larger than 100MB are partitioned into 20MB parts.
   - Each part is uploaded with its own presigned part URL.
   - Once all parts finish, `complete_multipart_upload` combines them.
   - If an upload is cancelled, `abort_multipart_upload` runs to prevent storage charges for incomplete chunks.

## Required Environment Variables

```env
B2_S3_ENDPOINT=https://s3.us-east-005.backblazeb2.com
B2_REGION=us-east-005
B2_BUCKET_NAME=lensvault-storage
B2_KEY_ID=your_backblaze_key_id
B2_APPLICATION_KEY=your_backblaze_application_key
B2_LOCAL_FALLBACK=False
```

## CORS Configuration on Backblaze B2 Bucket

In the Backblaze B2 Console, set the CORS rules for your bucket:

```json
[
  {
    "corsRuleName": "AllowLensVaultUploads",
    "allowedOrigins": [
      "https://yourdomain.com",
      "http://localhost:5173"
    ],
    "allowedOperations": [
      "s3_put",
      "s3_get",
      "s3_head",
      "s3_delete"
    ],
    "allowedHeaders": [
      "*"
    ],
    "exposeHeaders": [
      "ETag"
    ],
    "maxAgeSeconds": 3600
  }
]
```
