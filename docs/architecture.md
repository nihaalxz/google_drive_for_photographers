# LensVault System Architecture

LensVault is an enterprise-grade cloud storage and client delivery SaaS designed specifically for photographers, photography studios, and freelance photo editors.

## Architecture Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    LENSVAULT FRONTEND                                   |
|                (SvelteKit 5 + TypeScript + Tailwind CSS + Lucide Icons)                 |
|                                                                                         |
|  - Drive Explorer: Grid/List views, nested breadcrumb navigation, bulk actions          |
|  - Upload Manager: Direct-to-B2 S3 presigned PUT / multipart uploads, progress tracking |
|  - Image Viewer: High-res lightbox, keyboard navigation, EXIF parameter inspection      |
|  - Client Galleries: Proofing portal (/share/[token]) with favorites and downloads      |
|  - Settings & Storage: Visual storage meter, light/dark themes, workspace management    |
+------------------------------------+----------------------------------------------------+
                                     |
                          REST APIs / JSON / Cookies
                                     |
+------------------------------------v----------------------------------------------------+
|                                    DJANGO BACKEND                                       |
|             (Django REST Framework, Session & Cookie Auth, PyMySQL, Boto3)              |
|                                                                                         |
|  apps/accounts/   -> User model, authentication, profile, password security             |
|  apps/workspaces/ -> Studio workspaces, role memberships, quota management              |
|  apps/folders/    -> Hierarchical folder trees, breadcrumbs, soft-delete                 |
|  apps/files/      -> FileAsset metadata, EXIF parameters, trash/restore, search         |
|  apps/storage/    -> B2 S3 client, presigned URL generator, multipart lifecycle        |
|  apps/albums/     -> Client proofing collections, cover assignment                      |
|  apps/sharing/    -> Share links, token authorization, password hashing, expiry         |
|  apps/activity/   -> Audit logs for security, uploads, deletions                        |
+---------------------+---------------------------------------------+---------------------+
                      |                                             |
             Direct S3 Presigned Upload                    Authoritative Metadata
                      |                                             |
+---------------------v-------------+             +-----------------v---------------------+
|         BACKBLAZE B2 (S3 API)     |             |                MYSQL                  |
|   - Private Encrypted Bucket      |             |   - User & Workspace records          |
|   - Presigned Direct PUT / Part   |             |   - Hierarchical Folders & Files      |
|   - Controlled Expiration Links   |             |   - Albums & Share Tokens             |
|   - Boto3 SigV4 signature         |             |   - Storage Accounting Ledger         |
+-----------------------------------+             +---------------------------------------+
```

## Core Modules

### 1. Direct-to-B2 Storage Protocol
Unlike generic web apps that proxy multi-gigabyte files through the web application worker (causing memory exhaustion and timeout errors), LensVault implements a direct browser-to-B2 S3 upload pattern:
1. Client requests an upload session from Django.
2. Django validates workspace quota and signs a restricted S3 Presigned PUT URL.
3. Client streams bytes directly to Backblaze B2.
4. Client notifies Django upon completion.
5. Django validates object existence via `head_object` and records authoritative metadata and storage usage in MySQL.

### 2. Photography-Centric EXIF Metadata Pipeline
LensVault extracts and indexes camera parameters (body, lens model, f-stop, shutter speed, ISO, focal length, capture timestamp) alongside dimensions and megapixel metrics. Supported formats include JPEG, PNG, WebP, TIFF, MP4, and RAW formats (CR2, CR3, NEF, ARW, DNG, RAF).

### 3. Client Proofing Galleries
Photographers can curate albums and generate shareable links with unguessable tokens (`/share/[token]`), optional password protection (PBKDF2), and client favorite selections.

### 4. Visual Design Language
LensVault adheres to strict non-negotiable visual guidelines:
- Zero gradients, glowing orbs, or glassmorphism.
- Zero emojis.
- Semantic light and dark theme tokens.
- Restrained, purposeful micro-animations.
