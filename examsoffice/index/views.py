from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.


def index_view(request):
    template = "index.html"
    message = "Welcome to ECE Exams Office"
    context = {"message": message}
    return render(request, template, context)


def download_info(request):
    template = "download_info.html"
    next_url = request.GET["next"] or None
    print("This is the next url", next_url)
    return render(request, template, {"next": next_url})


def general_messages(request):
    template = "general_messages.html"
    return render(request, template, {})
