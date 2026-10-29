# LensVault — Premium Photographer Cloud Storage SaaS

LensVault is a professional, high-performance cloud storage and client delivery platform built specifically for photographers, photography studios, and freelance photo editors.

Combining the organizational familiarity of Google Drive with the raw speed of direct-to-S3 Backblaze B2 uploads and native camera EXIF inspection, LensVault is engineered to manage high-resolution photographic libraries and uncompressed RAW digital negatives.

---

## Key Features

- **Direct-to-B2 S3 Uploads**: Files stream directly from the browser to private Backblaze B2 buckets using AWS SigV4 Presigned PUT and Multipart URLs. The backend web server never bottlenecks or proxies multi-gigabyte transfers.
- **Native Camera EXIF Engine**: Automatically indexes camera bodies, prime/zoom lenses, apertures, shutter speeds, ISO parameters, focal lengths, and timestamps for CR2, CR3, NEF, ARW, DNG, and standard image formats.
- **Client Proofing Galleries**: Photographers can curate client albums, configure expiration dates, add optional password protection, and generate unguessable share links (`/share/[token]`). Clients can mark favorites and download authorized assets.
- **Zero-Gradient Visual Design**: Strict professional aesthetic adhering to high-contrast monochrome design tokens, crisp typography, and pure Lucide vector icons. Zero emojis, zero glowing orbs, zero fake analytics.
- **Hierarchical Drive**: Multi-level nested folders with breadcrumbs, drag-and-drop uploads, instant search, sorting, multi-selection, and bulk actions (star, trash, download, move).
- **Storage Accounting Ledger**: Authoritative quota tracking with visual format breakdown (RAW master archives, JPEGs, videos, other).
- **cPanel Deployment Ready**: Native support for cPanel Phusion Passenger WSGI (`passenger_wsgi.py`), MySQL databases via PyMySQL, and SvelteKit static or Node.js hosting.

---

## Technology Stack

- **Frontend**: SvelteKit 5, TypeScript, Tailwind CSS, Lucide Icons (`@lucide/svelte`), Zod.
- **Backend**: Python 3.12, Django 6 / 5, Django REST Framework, django-environ, PyMySQL, Boto3.
- **Object Storage**: Backblaze B2 S3-Compatible API (with local fallback simulation for zero-config offline development).
- **Database**: MySQL 8.0+ in production; SQLite supported out of the box for tests and local development.
- **Deployment**: cPanel compatible via Passenger WSGI and SvelteKit build adapter.

---

## Quick Start (Local Development)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

*Demo User Credentials:*
- **Email**: `demo@lensvault.com`
- **Password**: `Password123!`
- **Client Gallery Token**: `lake-como-sarah-james-2026`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## Running Verification Tests

### Backend Unit & Integration Tests:
```bash
cd backend
pytest -v --ds=config.settings tests/
```

### Frontend Type Check & Production Build:
```bash
cd frontend
npm run check
npm run build
```

---

## Documentation

- [System Architecture](docs/architecture.md)
- [REST API Reference](docs/api.md)
- [Security Model & Isolation](docs/security.md)
- [Backblaze B2 S3 Integration](docs/backblaze-b2.md)
- [cPanel Deployment Guide](docs/deployment-cpanel.md)
