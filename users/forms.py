from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
#from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class SignupForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username","email","first_name","last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    

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

