from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("testy.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
    path("bulls/", include("testy2.urls")),
]
# docker run -p 6379:6379 -d redis:5


#rm -f ./.git/index.lock
#cd .git
#del index.git
#del index.lock