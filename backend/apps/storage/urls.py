from django.urls import path, re_path
from .views import (
    CreateUploadSessionView,
    CompleteUploadSessionView,
    AbortUploadSessionView,
    MockUploadHandlerView,
    MockDownloadHandlerView
)

urlpatterns = [
    path('upload-session/', CreateUploadSessionView.as_view(), name='upload-session'),
    path('upload-complete/', CompleteUploadSessionView.as_view(), name='upload-complete'),
    path('upload-abort/', AbortUploadSessionView.as_view(), name='upload-abort'),
    re_path(r'^mock-upload/(?P<object_key>.+)$', MockUploadHandlerView.as_view(), name='mock-upload'),
    re_path(r'^mock-download/(?P<object_key>.+)$', MockDownloadHandlerView.as_view(), name='mock-download'),
]
