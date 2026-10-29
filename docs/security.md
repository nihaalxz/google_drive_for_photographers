# LensVault Security Architecture

This document describes the security protocols, permissions, object isolation, and cryptographic protections implemented across LensVault.

## 1. Multi-Tenant Workspace Perimeter

Every asset (folders, file assets, albums, and storage allocations) belongs strictly to a `Workspace`.

- **Object-Level Authorization**: Every endpoint verifies that the authenticated user possesses active membership in the target workspace via `workspace__memberships__user = request.user`.
- **Foreign Key Guarding**: It is impossible to guess, enumerate, or access files belonging to another workspace. Accessing an unowned ID yields a `404 Not Found`, giving zero indication of resource existence.

## 2. Direct-to-B2 Storage Security

- **Private Buckets**: The Backblaze B2 bucket is private. Direct access via public HTTP URLs is impossible.
- **Short-Lived Signed URLs**: Downloads and previews use AWS SigV4 signed URLs with expiration bounded between 1 to 2 hours.
- **Hidden Application Keys**: The frontend never receives Backblaze application keys or credentials. All signing occurs server-side in Django.
- **Content-Disposition Sandboxing**: Download URLs explicitly set `ResponseContentDisposition: attachment; filename="..."` to prevent malicious payloads from executing in the browser context.

## 3. Client Proofing Galleries & Token Cryptography

- **Unguessable Tokens**: Share links use high-entropy cryptographically secure random tokens (`secrets.token_urlsafe(24)`).
- **Password Protection**: Optional client gallery passwords are never stored in plaintext. They are hashed using Django's PBKDF2 with SHA-256 algorithm.
- **Expiration Enforcement**: Access attempts on expired links receive HTTP 410 Gone immediately.

## 4. Session & Cookie Security

- **HttpOnly Cookies**: Session cookies are marked `HttpOnly` and `SameSite='Lax'`.
- **CSRF Defense**: All mutating requests (POST, PUT, PATCH, DELETE) enforce `X-CSRFToken` validation.
- **Password Strength**: Minimum 8 characters enforced with Django's password validation framework.

## 5. Audit Logging

Sensitive actions (user registration, folder creation, file uploads, file trashing, permanent deletions, and link generation) are appended to an immutable `ActivityLog` ledger recording timestamp, user, action, and target ID.
