from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "chat/index1.html")


def new(request):
    return HttpResponse("new ")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
