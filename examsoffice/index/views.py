from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index_view(request):
    template_name = 'index.html'
    message = "This is the Home Page!"
    context = {'message': message}
    return render(request, template_name, context)
