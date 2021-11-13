from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.

def index_view(request):
    template_name = 'index.html'
    message = "This is the Home Page!"
    context = {'message': message}
    return render(request, template_name, context)

def download_info(request):
    template = 'download_info.html'
    next_url = request.GET['next'] or None
    print("This is the next url",next_url)
    return render(request, template, {'next':next_url})