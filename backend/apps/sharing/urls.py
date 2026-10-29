from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShareLinkViewSet, PublicShareView

router = DefaultRouter()
router.register(r'links', ShareLinkViewSet, basename='share-links')

urlpatterns = [
    path('public/<str:token>/', PublicShareView.as_view(), name='public-share'),
] + router.urls
