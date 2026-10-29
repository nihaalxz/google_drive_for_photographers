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

# Auto-detect public web root for lensvault.texasholidayssa.com or fallback
if [ -z "$PUBLIC_HTML" ]; then
  if [ -d "$HOME/lensvault.texasholidayssa.com" ]; then
    PUBLIC_HTML="$HOME/lensvault.texasholidayssa.com"
  elif [ -d "$HOME/public_html/lensvault.texasholidayssa.com" ]; then
    PUBLIC_HTML="$HOME/public_html/lensvault.texasholidayssa.com"
  elif [ -d "$HOME/lensvault.hevora.io" ]; then
    PUBLIC_HTML="$HOME/lensvault.hevora.io"
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
  mkdir -p "$PUBLIC_HTML"
  
  # Copy built files (including .htaccess and _app) to public_html
  cp -r "$FRONTEND_DIR/build/." "$PUBLIC_HTML/"
  
  echo "Frontend successfully synced to $PUBLIC_HTML"
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
