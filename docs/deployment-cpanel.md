# LensVault: cPanel Deployment Guide

This document details the production deployment process for LensVault on a standard cPanel hosting environment with CloudLinux / Phusion Passenger support, Python 3.11+, Node.js, and MySQL.

---

## 1. System Requirements & Architecture

- **cPanel Features**:
  - *Setup Python App* (Phusion Passenger WSGI)
  - *Setup Node.js App* (or static `public_html` hosting)
  - *MySQL Database Wizard*
  - *Cron Jobs*
  - *SSL/TLS Status* (Let's Encrypt / AutoSSL)
- **Runtimes**:
  - Python: 3.11 or 3.12
  - Node.js: 20 LTS or 22 LTS
  - MySQL: 8.0+ or MariaDB 10.5+
- **Object Storage**:
  - Backblaze B2 Bucket with S3-compatible application key (Read, Write, List, Delete)

---

## 2. MySQL Database Setup

1. Log in to cPanel.
2. Navigate to **MySQL Databases** or **MySQL Database Wizard**.
3. Create a new database: e.g. `cpaneluser_lensvault`.
4. Create a new database user: e.g. `cpaneluser_lvuser` with a strong random password.
5. Assign **All Privileges** to `cpaneluser_lvuser` on `cpaneluser_lensvault`.
6. Note the database connection string:
   ```env
   DATABASE_URL=mysql://cpaneluser_lvuser:YourStrongPassword@localhost:3306/cpaneluser_lensvault
   ```
   *Note: LensVault automatically uses PyMySQL (`pymysql.install_as_MySQLdb()`), avoiding the requirement for compiled C extensions on cPanel.*

## 3. Git-Based Setup & Deployment Workflow

### Step 3.1: Clone via cPanel "Git™ Version Control" (or SSH)

#### Method A: Using cPanel GUI (Git™ Version Control)
1. In cPanel, navigate to the **Files** section and click **Git™ Version Control**.
2. Click the blue **Create** button.
3. Configure the clone parameters:
   - **Clone URL**: `https://github.com/nihaalxz/google_drive_for_photographers.git`
     *(Note: If the repository is private, see Section 3.5 below for setting up SSH deploy keys).*
   - **Repository Path**: `lensvault` (this will clone the code to `/home/cpaneluser/lensvault`).
   - **Repository Name**: `lensvault`.
4. Click **Create**.

#### Method B: Using cPanel Terminal / SSH
Alternatively, open cPanel **Terminal** or connect via SSH:
```bash
cd ~
git clone https://github.com/nihaalxz/google_drive_for_photographers.git lensvault
```

---

## 4. Backend Configuration (Django + Passenger WSGI)

### Step 4.1: Configure Python App in cPanel
1. Open cPanel **Setup Python App**.
2. Click **Create Application**.
3. Configure the fields:
   - **Python version**: `3.11` or `3.12`
   - **Application root**: `lensvault/backend`
   - **Application URL**: `api.yourdomain.com` (or `yourdomain.com/api`)
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **Create**.

### Step 4.2: Production Environment (.env)
In cPanel **File Manager** or Terminal, create `/home/texastravels/lensvault/backend/.env`:
```env
DEBUG=False
SECRET_KEY=tBqEQDfyJ-EWKqc4hkMOildUIThcT1qJKQZ0yP1bv1EX2oqHQVUjsBYsPqWvjmA6sd0
ALLOWED_HOSTS=lensvault.hevora.io,api.lensvault.hevora.io,localhost,127.0.0.1

DATABASE_URL=mysql://texastravels_lensvault:texastravels_lensvault@localhost:3306/texastravels_lensvault

CORS_ALLOWED_ORIGINS=https://lensvault.hevora.io,https://api.lensvault.hevora.io
CSRF_TRUSTED_ORIGINS=https://lensvault.hevora.io,https://api.lensvault.hevora.io

B2_S3_ENDPOINT=https://s3.eu-central-003.backblazeb2.com
B2_REGION=eu-central-003
B2_BUCKET_NAME=hevoracloudstorage
B2_KEY_ID=003e8b9198420200000000001
B2_APPLICATION_KEY=K003yCglgGKINtIW9sTGpF11cWhExFY
B2_LOCAL_FALLBACK=False
DEFAULT_WORKSPACE_QUOTA_BYTES=10737418240
```

---

## 5. Automated Deployment with `deploy.sh`

LensVault includes a one-step deployment script `deploy.sh` that automates git pulling, backend dependencies, database migrations, static asset collection, frontend building, syncing to `public_html/`, and Phusion Passenger WSGI reloading.

### Running a Deployment:
From the cPanel **Terminal** or SSH:
```bash
cd ~/lensvault
bash deploy.sh
```

### Auto-Deploy via cPanel Git Version Control & Webhooks:
1. In cPanel **Git™ Version Control**, click **Manage** on the `lensvault` repository.
2. Select the **Deploy** tab. The repository includes `.cpanel.yml` which automatically invokes `deploy.sh`.
3. To trigger deployment automatically on every `git push origin main`:
   - Copy the **Webhook URL** provided in cPanel Git Version Control.
   - Go to your GitHub repository: **Settings** > **Webhooks** > **Add webhook**.
   - Paste the Payload URL, set Content type to `application/json`, and select **Just the push event**.
   - Every time you push to GitHub, cPanel automatically pulls and runs `deploy.sh`!

### 5.3: Setting Up SSH Deploy Keys (For Private Repositories)
If your GitHub repository is private:
1. In cPanel, open **SSH Access** > **Manage SSH Keys** > **Generate a New Key**.
2. Name it `id_rsa_lensvault` and leave the passphrase empty.
3. Click **View/Edit** on the Public Key and copy the key string.
4. Go to your GitHub repository > **Settings** > **Deploy keys** > **Add deploy key**.
5. Paste the key and check **Allow write access** (optional, read-only is sufficient).
6. In cPanel **Git™ Version Control**, use the SSH clone URL:
   `git@github.com:nihaalxz/google_drive_for_photographers.git`

---

## 6. Frontend Routing (`public_html/.htaccess`)

The frontend build is output directly into `public_html/`. The included `frontend/static/.htaccess` handles SPA client-side routing and forces HTTPS:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /

  # Force HTTPS
  RewriteCond %{HTTPS} off
  RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

  # Don't rewrite actual files or directories
  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]

  # SvelteKit SPA fallback to index.html
  RewriteRule ^ index.html [L]
</IfModule>
```

---

## 7. Automated Maintenance Cron Jobs

In cPanel **Cron Jobs**, set up the following automated tasks:

1. **Daily Database Backup (Every day at 02:00 AM)**:
   ```bash
   mysqldump -u cpaneluser_lvuser -p'YourPassword' cpaneluser_lensvault | gzip > /home/cpaneluser/backups/db_$(date +\%F).sql.gz
   ```

2. **Storage Ledger Reconciliation & Orphan Cleanup (Every day at 04:00 AM)**:
   ```bash
   source /home/cpaneluser/virtualenv/lensvault_backend/3.12/bin/activate && python /home/cpaneluser/lensvault_backend/manage.py clearsessions
   ```

---

## 6. Verification Checklist

- [ ] Health check endpoint responds with status 200 at `https://api.yourdomain.com/api/v1/health/`
- [ ] Database reports `'connected'` and storage reports `'backblaze_b2'`
- [ ] User registration and session cookies work over HTTPS
- [ ] Direct presigned PUT upload streams to Backblaze B2 without passing through cPanel WSGI memory
- [ ] Client proofing galleries are accessible at `https://yourdomain.com/share/<token>`
