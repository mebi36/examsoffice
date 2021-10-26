from django.shortcuts import render

# Create your views here.
def students_menu(request):
    transcript_name = 'students/menu.html'

    return render(request, transcript_name, {})
