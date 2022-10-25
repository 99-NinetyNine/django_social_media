from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url


urlpatterns = [
    path("big/", views.index, name="index_page2"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
