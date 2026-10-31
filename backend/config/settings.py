import os
from pathlib import Path
import environ
import pymysql

# Enable PyMySQL as MySQLdb for MySQL on cPanel & local development
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'lensvault-insecure-dev-secret-key-please-change-in-production-12345'),
    ALLOWED_HOSTS=(list, ['*']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:5173', 'http://127.0.0.1:5173']),
    CSRF_TRUSTED_ORIGINS=(list, ['http://localhost:5173', 'http://127.0.0.1:5173']),
    B2_S3_ENDPOINT=(str, 'https://s3.us-east-005.backblazeb2.com'),
    B2_REGION=(str, 'us-east-005'),
    B2_BUCKET_NAME=(str, 'lensvault-storage'),
    B2_KEY_ID=(str, ''),
    B2_APPLICATION_KEY=(str, ''),
    B2_LOCAL_FALLBACK=(bool, True),
    DEFAULT_WORKSPACE_QUOTA_BYTES=(int, 10737418240),
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Reverse Proxy / SSL settings for cPanel / LiteSpeed / Passenger
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

AUTH_USER_MODEL = 'accounts.User'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'corsheaders',
    'rest_framework',
    
    # LensVault Apps
    'apps.accounts',
    'apps.workspaces',
    'apps.folders',
    'apps.files',
    'apps.storage',
    'apps.albums',
    'apps.sharing',
    'apps.activity',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security & Reverse Proxy (cPanel / LiteSpeed / Passenger)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%SZ',
}

# CORS & CSRF Settings
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', default='Lax')
CSRF_COOKIE_SAMESITE = env('CSRF_COOKIE_SAMESITE', default='Lax')
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=not DEBUG)
SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', default=None)
CSRF_COOKIE_DOMAIN = env('CSRF_COOKIE_DOMAIN', default=None)
CSRF_COOKIE_HTTPONLY = False  # Allows SvelteKit client to read csrftoken for mutation headers

# Backblaze B2 Object Storage
B2_S3_ENDPOINT = env('B2_S3_ENDPOINT')
B2_REGION = env('B2_REGION')
B2_BUCKET_NAME = env('B2_BUCKET_NAME')
B2_KEY_ID = env('B2_KEY_ID')
B2_APPLICATION_KEY = env('B2_APPLICATION_KEY')
B2_LOCAL_FALLBACK = env('B2_LOCAL_FALLBACK')

# Storage Quota
DEFAULT_WORKSPACE_QUOTA_BYTES = env('DEFAULT_WORKSPACE_QUOTA_BYTES')
