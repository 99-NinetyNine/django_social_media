from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404, Http404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import modelformset_factory
from django.views.generic.dates import (
    YearArchiveView,
    MonthArchiveView,
    WeekArchiveView,
)
from django.views import View
from django.views import View


from django.views.generic import (
    View,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.contrib.auth.views import LogoutView
from django.views.generic.list import MultipleObjectMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
import datetime
import random

from .forms import (
    SignupForm,
    UserEditForm,
    ProfilePictureEditForm,
)

from testy.models import Contact
from .models import Profile


@login_required
def EditProfile(request):
    if request.method == "POST":
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        pp_change = ProfilePictureEditForm(
            data=request.POST or None,
            instance=request.user.profile,
            files=request.FILES,
        )
        if user_form.is_valid() and pp_change.is_valid():
            form1 = user_form.save(commit=False)
            form2 = pp_change.save(commit=False)
            form1.user, form2.user = request.user
            form1.save()
            form2.save()

            messages.success(request, "Your profile has been updated successfully.")
            return HttpResponseRedirect(
                reverse("profile_view", args=[request.user.username])
            )

    else:
        user_form = UserEditForm(instance=request.user)
        pp_change = ProfilePictureEditForm(instance=request.user.profile)

    is_private = False
    if request.user.profile.private:
        is_private = True
    context = {
        "is_private": is_private,
        "user_form": user_form,
        "pp_change": pp_change,
    }
    return render(request, "users/profile_edit.html", context)
    # return HttpResponseRedirect(request.user.profile.get_absolute_url())


@login_required
def ChangeProfilePhoto(request):
    if request.method == "POST":
        pp_change = ProfilePictureEditForm(
            data=request.POST or None,
            instance=request.user.profile,
            files=request.FILES,
        )
        if pp_change.is_valid():
            f = pp_change.save(commit=False)
            f.user = request.user
            f.save()
            return HttpResponseRedirect(
                reverse("profile_view", args=[request.user.username])
            )

    else:
        pp_change = ProfilePictureEditForm(instance=request.user.profile)

    context = {
        "pp_change": pp_change,
    }
    print(pp_change)
    return render(request, "users/pp_change.html", context)


@login_required
def ProfileVisibility(request):
    user = get_object_or_404(User, id=request.POST.get("id"))
    if not user == request.user:
        raise Http404()
    is_private = False
    if user.profile.private:
        is_private = False
    elif not user.profile.private:
        is_private = True

    Profile.objects.filter(user=user).update(private=is_private)
    context = {
        "is_private": is_private,
    }
    if request.is_ajax():
        html = render_to_string("users/private_account.html", context, request=request)
        return JsonResponse({"form": html})


@login_required
def PrivacySetting(request):
    is_private = False
    if request.user.profile.private:
        is_private = True
    context = {
        "is_private": is_private,
    }
    return render(request, "users/privacy_setting.html", context)
    # return HttpResponseRedirect(request.ser.profile.get_absolute_url())


def signupview(request):
    if request.user.is_authenticated:
        # return reverse("profile_view", args=["request.user.username"])
        return HttpResponseRedirect("/")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            x = form.save(commit=False)
            x.save()
            return redirect("index_page")

    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})


class MyLogoutView(LogoutView):
    template_name = "users/home.html"
    extra_context = {"form": AuthenticationForm()}


"""

class Signup(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "signup.html", {"form": form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create an inactive user with no password:
            user = form.save(commit=False)
            user.is_active = False
            user.set_unusable_password()
            user.save()

            # Send an email to the user with the token:
            mail_subject = "Activate your account."
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # token = account_activation_token.make_token(user)
            activation_link = "{0}/?uid={1}&token{2}".format(current_site, uid,)
            # token)
            message = "Hello {0},\n {1}".format(user.username, activation_link)
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )


class Activate(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user and login:
            user.is_active = True
            user.save()
            login(request, user)

            form = PasswordChangeForm(request.user)
            return render(request, "activation.html", {"form": form})

        else:
            return HttpResponse("Activation link is invalid!")

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Important, to update the session with the new password
            return HttpResponse("Password changed successfully")

 """
