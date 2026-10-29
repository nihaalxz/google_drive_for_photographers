# LensVault REST API Reference

All endpoints are versioned under `/api/v1/`.

## Authentication & Accounts (`/api/v1/auth/`)

- `POST /api/v1/auth/register/`
  - Body: `{ email, username, password, full_name, workspace_name }`
  - Creates user and personal workspace. Logs in session.
- `POST /api/v1/auth/login/`
  - Body: `{ email, password }`
  - Sets session cookie and returns user profile + active workspace.
- `POST /api/v1/auth/logout/`
  - Terminates session.
- `GET /api/v1/auth/me/`
  - Returns authenticated user and workspace memberships.
- `PATCH /api/v1/auth/me/`
  - Updates profile: `{ full_name, bio, timezone }`.
- `POST /api/v1/auth/change-password/`
  - Body: `{ old_password, new_password }`.

---

## Workspaces (`/api/v1/workspaces/`)

- `GET /api/v1/workspaces/`
  - Lists workspaces user is a member of.
- `GET /api/v1/workspaces/{id}/storage_breakdown/`
  - Returns total limit, used bytes, available bytes, and breakdown by RAW, image, video, and other formats.
- `GET /api/v1/workspaces/{id}/members/`
  - Lists workspace members and roles.
- `POST /api/v1/workspaces/{id}/members/`
  - Invites/adds member: `{ email, role }`.

---

## Folders (`/api/v1/folders/`)

- `GET /api/v1/folders/?workspace_id={id}&parent_id={parent_or_root}`
  - Lists folders inside a given hierarchy.
- `POST /api/v1/folders/`
  - Body: `{ workspace_id, name, parent, color }`.
- `PATCH /api/v1/folders/{id}/`
  - Renames or edits folder.
- `DELETE /api/v1/folders/{id}/`
  - Soft-deletes folder and all descendant items into trash.
- `POST /api/v1/folders/{id}/restore/`
  - Restores folder and descendants from trash.
- `POST /api/v1/folders/{id}/toggle_star/`
  - Stars or unstars folder.
- `POST /api/v1/folders/{id}/move/`
  - Moves folder to new parent: `{ parent_id }`.

---

## Files (`/api/v1/files/`)

- `GET /api/v1/files/?workspace_id={id}&folder_id={id}&starred={bool}&deleted={bool}&type={image|video|raw}&q={search}&sort_by={field}&sort_direction={asc|desc}`
  - Paginated list of photography assets.
- `GET /api/v1/files/{id}/`
  - Detailed asset record with camera EXIF, resolution, and signed preview/download URLs.
- `PATCH /api/v1/files/{id}/`
  - Updates safe display name or metadata.
- `DELETE /api/v1/files/{id}/`
  - Moves file to trash.
- `POST /api/v1/files/{id}/restore/`
  - Restores file from trash.
- `DELETE /api/v1/files/{id}/permanent_delete/`
  - Permanently removes file from Backblaze B2 object storage and decrements storage usage ledger.
- `POST /api/v1/files/{id}/toggle_star/`
  - Stars or unstars file.
- `POST /api/v1/files/bulk_action/`
  - Body: `{ action: 'trash' | 'restore' | 'star' | 'unstar' | 'delete_permanent' | 'move', file_ids: [...] }`.

---

## Object Storage (`/api/v1/storage/`)

- `POST /api/v1/storage/upload-session/`
  - Body: `{ workspace_id, original_filename, file_size, mime_type, folder_id }`
  - Verifies quota, generates safe object key, returns presigned S3 upload URL or multipart part URLs.
- `POST /api/v1/storage/upload-complete/`
  - Body: `{ session_id, etag, parts, metadata: { camera_make, camera_model, f_stop, ... } }`
  - Verifies object existence in B2, creates `FileAsset`, and updates storage ledger.
- `POST /api/v1/storage/upload-abort/`
  - Aborts incomplete upload.

---

## Albums (`/api/v1/albums/`)

- `GET /api/v1/albums/?workspace_id={id}`
  - Lists curated albums.
- `POST /api/v1/albums/`
  - Body: `{ workspace_id, title, description, client_name, client_email, event_date }`.
- `GET /api/v1/albums/{id}/assets/`
  - Returns list of photos associated with album.
- `POST /api/v1/albums/{id}/add_assets/`
  - Body: `{ file_ids: [...] }`.
- `POST /api/v1/albums/{id}/remove_asset/`
  - Body: `{ file_id }`.
- `POST /api/v1/albums/{id}/set_cover/`
  - Body: `{ file_id }`.

---

## Sharing & Client Proofing (`/api/v1/sharing/`)

- `GET /api/v1/sharing/links/?workspace_id={id}`
  - Lists active share links.
- `POST /api/v1/sharing/links/`
  - Body: `{ workspace_id, title, target_type, album, folder, file_asset, password, expires_at, allow_downloads, allow_favorites }`.
- `DELETE /api/v1/sharing/links/{id}/`
  - Revokes share link.
- `GET /api/v1/sharing/public/{token}/`
  - Public endpoint. If password protected, requires `X-Share-Password` header.
- `POST /api/v1/sharing/public/{token}/`
  - Body: `{ action: 'favorite' | 'download', file_id }`.
