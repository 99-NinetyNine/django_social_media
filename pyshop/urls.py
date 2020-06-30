from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("chat/", include("chat.urls")),
    path("", include("testy.urls")),
    path("test/456/", include("testy.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
]
