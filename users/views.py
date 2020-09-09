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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

import threading

import datetime
import random

from .forms import (
    SignupForm,
    UserEditForm,
    ProfilePictureEditForm,
)

from testy.models import Contact
from .models import Profile



class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        form = SignupForm()
        context={
            'form':form,
        }
        return render(request, 'users/signup.html',context)

    def post(self, request):
        context = {

            'data': request.POST,
            'has_error': False
        }
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #user=x.user
            user.is_active=False
            user.save()
                
            current_site = get_current_site(request)
            email_subject = 'Active your Account'
            message = render_to_string('users/activate.html',
                                    {
                                        'user': user,
                                        'domain': current_site.domain,
                                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                        'token': generate_token.make_token(user)
                                    }
                                    )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email]
            )

            EmailThread(email_message).start()
            messages.add_message(request, messages.SUCCESS,
                                'account created succesfully')

            return render(request,'users/activate_account.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request,'account activated successfully')
            return redirect('login')
        return render(request, 'users/activate_failed.html', status=401)



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


class MyLogoutView(LogoutView):
    template_name = "users/home.html"
    extra_context = {"form": AuthenticationForm()}


