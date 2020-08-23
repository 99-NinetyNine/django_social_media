from django import forms
from .models import (
    Nature,
    Comments,
    Story,
    Test,
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


class NatureEditForm(forms.ModelForm):
    class Meta:
        model = Nature
        fields = [
            "caption",
            "hide_post",
            "restrict_comment",
        ]


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = [
            "photo",
        ]

        labels = {
            "photo": "Photo/Video",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        self.fields["comment"].widget.attrs["rows"] = 1
        # self.fields["comment"].widget.attrs["columns"] = 15


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
