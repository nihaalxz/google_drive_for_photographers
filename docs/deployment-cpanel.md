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

---

## 3. Backend Deployment (Django + Passenger WSGI)

### Step 3.1: Upload Backend Files
1. In cPanel **File Manager** (or via SFTP/Git), create the directory `/home/cpaneluser/lensvault_backend/`.
2. Upload the `backend/` files to this directory (excluding `venv/`, `__pycache__/`, and `.git/`).

### Step 3.2: Configure Python App in cPanel
1. Open cPanel **Setup Python App**.
2. Click **Create Application**.
3. Configure the fields:
   - **Python version**: `3.11` or `3.12`
   - **Application root**: `lensvault_backend`
   - **Application URL**: `api.yourdomain.com` (or `yourdomain.com/api`)
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **Create**.

### Step 3.3: Install Dependencies & Run Migrations
1. In the Python App dashboard, copy the virtualenv activation command shown at the top, for example:
   ```bash
   source /home/cpaneluser/virtualenv/lensvault_backend/3.12/bin/activate && cd /home/cpaneluser/lensvault_backend
   ```
2. Log in via SSH or open the cPanel **Terminal**:
   ```bash
   source /home/cpaneluser/virtualenv/lensvault_backend/3.12/bin/activate
   cd /home/cpaneluser/lensvault_backend
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Create the production `.env` file in `/home/cpaneluser/lensvault_backend/.env`:
   ```env
   DEBUG=False
   SECRET_KEY=generate-a-random-50-character-secret-key-here
   ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

   DATABASE_URL=mysql://cpaneluser_lvuser:YourPassword@localhost:3306/cpaneluser_lensvault

   CORS_ALLOWED_ORIGINS=https://yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

   B2_S3_ENDPOINT=https://s3.us-east-005.backblazeb2.com
   B2_REGION=us-east-005
   B2_BUCKET_NAME=your-private-b2-bucket
   B2_KEY_ID=your_backblaze_key_id
   B2_APPLICATION_KEY=your_backblaze_application_key
   B2_LOCAL_FALLBACK=False
   ```
4. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
5. Seed initial admin user if desired:
   ```bash
   python manage.py createsuperuser
   ```

### Step 3.4: Restart Python App
In cPanel **Setup Python App**, click **Restart** to load the new code and environment.

---

## 4. Frontend Deployment (SvelteKit)

### Option A: Server-Rendered (Node.js via cPanel Setup Node.js App)
1. In `frontend/package.json`, ensure `@sveltejs/adapter-node` is used.
2. Build locally or in cPanel:
   ```bash
   npm run build
   ```
3. Upload `build/`, `package.json`, and `package-lock.json` to `/home/cpaneluser/lensvault_frontend/`.
4. In cPanel **Setup Node.js App**:
   - Application root: `lensvault_frontend`
   - Application startup file: `build/index.js`
   - Application URL: `yourdomain.com`
5. Click **Run NPM Install** and then **Restart**.

### Option B: Single Page Application (Static `public_html`)
1. In `frontend/`, run:
   ```bash
   npm run build
   ```
2. Copy the contents of the generated client bundle into your domain's `public_html/`.
3. Add this `.htaccess` file in `public_html/` to support client-side routing and reverse-proxy `/api/`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /

  # Force HTTPS
  RewriteCond %{HTTPS} off
  RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

  # Proxy /api/ to Passenger WSGI backend if separate port/subdomain
  # RewriteRule ^api/(.*)$ https://api.yourdomain.com/api/$1 [P,L]

  # SvelteKit Single Page Application Routing Fallback
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule ^ index.html [L]
</IfModule>
```

---

## 5. Automated Maintenance Cron Jobs

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
