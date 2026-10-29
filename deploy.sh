#!/bin/bash
# ==============================================================================
# LensVault - Automated cPanel Deployment Script
# ==============================================================================
# Usage:
#   bash deploy.sh
#
# What this script does:
#   1. Pulls the latest commits from Git origin/main
#   2. Detects and activates the cPanel Python virtual environment
#   3. Installs any updated Python backend dependencies
#   4. Runs Django database migrations
#   5. Collects Django static files
#   6. Builds the SvelteKit frontend (or deploys prebuilt assets)
#   7. Syncs frontend build files to public_html/
#   8. Restarts Phusion Passenger WSGI (Django backend)
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Allow command-line argument to specify target document root: bash deploy.sh /path/to/docroot
if [ -n "$1" ]; then
  PUBLIC_HTML="$1"
fi

# Auto-detect public web root for lensvault.texasholidayssa.com or fallback
if [ -z "$PUBLIC_HTML" ]; then
  if [ -d "$HOME/lensvault.texasholidayssa.com" ]; then
    PUBLIC_HTML="$HOME/lensvault.texasholidayssa.com"
  elif [ -d "$HOME/public_html/lensvault.texasholidayssa.com" ]; then
    PUBLIC_HTML="$HOME/public_html/lensvault.texasholidayssa.com"
  elif [ -d "$HOME/public_html/lensvault" ]; then
    PUBLIC_HTML="$HOME/public_html/lensvault"
  elif [ -d "$HOME/lensvault_frontend" ]; then
    PUBLIC_HTML="$HOME/lensvault_frontend"
  else
    PUBLIC_HTML="$HOME/public_html"
  fi
fi

echo "=================================================="
echo " Starting LensVault Deployment"
echo " Project Root: $PROJECT_ROOT"
echo " Target Document Root: $PUBLIC_HTML"
echo "=================================================="

# ------------------------------------------------------------------------------
# 1. Pull Latest Changes from Git
# ------------------------------------------------------------------------------
echo ""
echo "--> [1/6] Pulling latest changes from git..."
cd "$PROJECT_ROOT"
git pull origin main

# ------------------------------------------------------------------------------
# 2. Locate & Activate Python Virtual Environment
# ------------------------------------------------------------------------------
echo ""
echo "--> [2/6] Activating Python virtual environment..."

VENV_ACTIVATED=false

# Check common cPanel Python virtualenv locations
CANDIDATE_VENVS=(
  "$HOME/virtualenv/lensvault/backend/3.12/bin/activate"
  "$HOME/virtualenv/lensvault/backend/3.11/bin/activate"
  "$HOME/virtualenv/lensvault_backend/3.12/bin/activate"
  "$HOME/virtualenv/lensvault_backend/3.11/bin/activate"
  "$BACKEND_DIR/venv/bin/activate"
)

for venv_path in "${CANDIDATE_VENVS[@]}"; do
  if [ -f "$venv_path" ]; then
    echo "Found virtual environment: $venv_path"
    source "$venv_path"
    VENV_ACTIVATED=true
    break
  fi
done

if [ "$VENV_ACTIVATED" = false ]; then
  # Try to find any virtualenv matching lensvault
  AUTO_VENV=$(find "$HOME/virtualenv" -name "activate" 2>/dev/null | grep -i "lensvault" | head -n 1 || true)
  if [ -n "$AUTO_VENV" ] && [ -f "$AUTO_VENV" ]; then
    echo "Auto-detected virtual environment: $AUTO_VENV"
    source "$AUTO_VENV"
    VENV_ACTIVATED=true
  fi
fi

if [ "$VENV_ACTIVATED" = false ]; then
  echo "WARNING: Could not auto-detect cPanel virtualenv."
  echo "Please verify Python App configuration in cPanel > Setup Python App."
fi

# ------------------------------------------------------------------------------
# 3. Backend: Dependencies, Migrations & Static Files
# ------------------------------------------------------------------------------
echo ""
echo "--> [3/6] Updating backend dependencies and database..."
cd "$BACKEND_DIR"

if [ "$VENV_ACTIVATED" = true ]; then
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  
  if [ -f ".env" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
    
    echo "Generating compressed thumbnails for newly uploaded or un-cached images..."
    python manage.py generate_thumbnails || true

    echo "Collecting backend static files..."
    python manage.py collectstatic --noinput || true
  else
    echo "NOTE: $BACKEND_DIR/.env not found yet. Skipping migrate/collectstatic."
    echo "Please copy .env.example to .env and configure your database."
  fi
fi

# ------------------------------------------------------------------------------
# 4. Frontend: Build Production Assets
# ------------------------------------------------------------------------------
echo ""
echo "--> [4/6] Building frontend assets..."
cd "$FRONTEND_DIR"

if command -v npm &> /dev/null; then
  echo "Running npm install..."
  npm install --quiet
  
  echo "Running npm run build..."
  npm run build
else
  echo "npm not found in PATH. Checking for prebuilt assets in frontend/build..."
fi

# ------------------------------------------------------------------------------
# 5. Deploy Frontend to public_html
# ------------------------------------------------------------------------------
echo ""
echo "--> [5/6] Syncing frontend build to $PUBLIC_HTML..."

if [ -d "$FRONTEND_DIR/build" ]; then
  # Ensure LiteSpeed and web server can traverse project directories
  chmod 755 "$PROJECT_ROOT" "$FRONTEND_DIR" "$FRONTEND_DIR/build" 2>/dev/null || true

  # Also copy to frontend root in case cPanel document root is set to lensvault/frontend
  cp -r "$FRONTEND_DIR/build/." "$FRONTEND_DIR/" 2>/dev/null || true

  # Candidate roots to sync to
  CANDIDATE_TARGETS=(
    "$PUBLIC_HTML"
    "$HOME/public_html/lensvault"
    "$HOME/public_html/lensvault.texasholidayssa.com"
    "$HOME/lensvault.texasholidayssa.com"
  )

  for target in "${CANDIDATE_TARGETS[@]}"; do
    if [ -n "$target" ] && [ -d "$target" ] && [ "$target" != "$FRONTEND_DIR/build" ] && [ "$target" != "$FRONTEND_DIR" ]; then
      echo "Syncing frontend assets to $target..."
      cp -r "$FRONTEND_DIR/build/." "$target/" 2>/dev/null || true
      find "$target" -maxdepth 2 -type d -exec chmod 755 {} + 2>/dev/null || true
      find "$target" -maxdepth 2 -type f -exec chmod 644 {} + 2>/dev/null || true
    fi
  done
  
  echo "Frontend assets deployed with full LiteSpeed permissions."
else
  echo "WARNING: $FRONTEND_DIR/build directory not found."
  echo "Make sure frontend was built before deploying."
fi

# ------------------------------------------------------------------------------
# 6. Restart Passenger WSGI
# ------------------------------------------------------------------------------
echo ""
echo "--> [6/6] Reloading Phusion Passenger Python App..."
mkdir -p "$BACKEND_DIR/tmp"
touch "$BACKEND_DIR/tmp/restart.txt"

echo ""
echo "=================================================="
echo " Deployment Complete!"
echo " Passenger WSGI signaled to reload via tmp/restart.txt"
echo "=================================================="
