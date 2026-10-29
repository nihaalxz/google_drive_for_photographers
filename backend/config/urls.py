from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from apps.storage.services.b2 import b2_service

def health_check(request):
    db_ok = True
    try:
        connection.cursor().execute("SELECT 1")
    except Exception as e:
        db_ok = False

    return JsonResponse({
        'status': 'healthy' if db_ok else 'degraded',
        'database': 'connected' if db_ok else 'disconnected',
        'storage_mode': 'backblaze_b2' if b2_service.has_credentials else 'local_fallback',
        'b2_bucket': b2_service.bucket_name,
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/workspaces/', include('apps.workspaces.urls')),
    path('api/v1/folders/', include('apps.folders.urls')),
    path('api/v1/files/', include('apps.files.urls')),
    path('api/v1/storage/', include('apps.storage.urls')),
    path('api/v1/albums/', include('apps.albums.urls')),
    path('api/v1/sharing/', include('apps.sharing.urls')),
    path('api/v1/activity/', include('apps.activity.urls')),
]
