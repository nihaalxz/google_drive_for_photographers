from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from django.views.static import serve
from apps.storage.services.b2 import b2_service

FRONTEND_BUILD_DIR = settings.BASE_DIR.parent / 'frontend' / 'build'

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

def serve_spa(request, resource=''):
    """
    Serves SvelteKit SPA frontend when Django/Passenger handles the root domain.
    """
    target = FRONTEND_BUILD_DIR / resource
    if resource and target.is_file():
        return serve(request, resource, document_root=str(FRONTEND_BUILD_DIR))
    
    index_file = FRONTEND_BUILD_DIR / 'index.html'
    if index_file.is_file():
        with open(index_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
            
    return JsonResponse({
        'name': 'LensVault API',
        'status': 'online',
        'message': 'Frontend static build not found. Run npm run build in frontend directory.'
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
    # Fallback to SPA client router
    re_path(r'^(?P<resource>.*)$', serve_spa, name='spa-fallback'),
]

