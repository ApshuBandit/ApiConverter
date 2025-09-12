

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/convert/", include("converter.urls")),
    path("",include("converter.urls")),

]
