from django.shortcuts import render
from results.models import Course
from .forms import CourseForm
from django.contrib import messages

def view(request):
    template = 'courses/view.html'
    courses_qs = Course.objects.all().order_by('-id')

    return render(request, template, {'courses': courses_qs })

def add(request):
    template = 'courses/add.html'
    context = {}

    if request.method == 'GET':
        form = CourseForm()
        context = {'form': form}
        return render(request, template, context)

    elif request.method == 'POST':
        form = CourseForm(request.POST)

        if not form.is_valid():
            messages.add_message(request, messages.ERROR,
                                    'Form entry invalid.',
                                    extra_tags='text-danger')
            context = {'form': form}
            return render(request, template, context)
        
        form.save()
        messages.add_message(request, messages.SUCCESS, "Save successful",
                            extra_tags='text-success')
        return render(request, template, {'form': form})