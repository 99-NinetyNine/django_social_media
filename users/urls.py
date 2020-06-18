from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("signup/", views.signupview, name="signup_page"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/home.html"),
        name="login",
    ),
    path("logout/", views.MyLogoutView.as_view(), name="logout",),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(template_name="users/pc.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="users/pr.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/prdone.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/prconfirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/prcomplete.html"
        ),
        name="password_reset_complete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
