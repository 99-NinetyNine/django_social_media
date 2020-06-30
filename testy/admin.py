from django.contrib import admin
from .models import (
    User,
    Nature,
    NatureImage,
    Comments,
    Notification,
    Contact,
    Test,
)

from users.models import Profile
from django.db import models
from django.forms import TextInput, Textarea


class NatureImageAdmin(admin.TabularInline):
    model = NatureImage


class CommentAdmin(admin.TabularInline):
    model = Comments


class NatureAdmin(admin.ModelAdmin):
    inlines = [
        NatureImageAdmin,
    ]


admin.site.register(Nature, NatureAdmin)
admin.site.register(NatureImage)
admin.site.register(Comments)
admin.site.register(Contact)
admin.site.register(Profile)
admin.site.register(Notification)

admin.site.register(Test)
