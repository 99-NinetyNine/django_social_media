from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django import forms
from django.http import Http404
from django.views.generic.dates import (
    YearArchiveView,
    MonthArchiveView,
    WeekArchiveView,
)
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def index(request):
    msg="We are working on this feature."
    context={
        "msg":msg,
    }
    return render(request,'testy2/hi.html',context)
