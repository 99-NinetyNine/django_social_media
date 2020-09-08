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
        auth_views.PasswordChangeView.as_view(template_name="users/pwd_change.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="users/pwd_reset.html"),
        name="password_reset",
    ),
    path("password_reset/done/",auth_views.PasswordResetDoneView.as_view(template_name="users/pwd_reset_done.html"),name="password_reset_done",),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="users/pwd_reset_confirm.html"),name="password_reset_confirm",),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/pwd_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("account/settings/", views.EditProfile, name="account_setting"),
    path("account/visibility/", views.ProfileVisibility, name="private_public"),
    path("change/photo/", views.ChangeProfilePhoto, name="change_profile"),
    path("profile/edit/", views.EditProfile, name="edit_profile"),
    path("profile/privacy/", views.PrivacySetting, name="privacy_setting"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
