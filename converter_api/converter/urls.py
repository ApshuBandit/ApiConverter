from django.urls import path
from .views import ImageConvertAPIView, upload_view

urlpatterns = [
    path("api/convert/", ImageConvertAPIView.as_view(), name="api-convert"),  # API endpoint
    path("", upload_view, name="upload"),  # сайт с формой
]
