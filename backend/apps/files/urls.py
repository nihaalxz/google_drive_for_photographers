from rest_framework.routers import DefaultRouter
from .views import FileAssetViewSet

router = DefaultRouter()
router.register(r'', FileAssetViewSet, basename='files')

urlpatterns = router.urls
