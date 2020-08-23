from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


SignupForm=UserCreationForm
    

class UserEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]


class ProfilePictureEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = [
            "user",
            "last_seen",
            "private",
        ]

