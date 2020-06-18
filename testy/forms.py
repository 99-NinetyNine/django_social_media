from django import forms
from .models import (
    Nature,
    Comments,
    Story,
)
from users.models import Profile
from django.contrib.auth.models import User


class NatureForm(forms.ModelForm):
    class Meta:
        model = Nature
        fields = [
            "caption",
        ]

        labels = {
            "caption": "Add Caption",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]


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
        ]


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = [
            "comment",
        ]


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = [
            "photo",
        ]

        labels = {
            "photo": "add your story",
        }
