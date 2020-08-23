from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("testy.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
]
# docker run -p 6379:6379 -d redis:5

