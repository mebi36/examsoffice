from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse

from .forms import (ProgressHistoryForm, 
                    StudentBioForm, 
                    )
from results.models import (LevelOfStudy, Student,
                            StudentProgressHistory, Session,)

# Create your views here.
def students_menu(request):
    transcript_name = 'students/menu.html'

    return render(request, transcript_name, {})

def search(request):
    if request.method == 'POST':
        if Student.is_valid_reg_no(request.POST['reg_no']):
            reg_no = request.POST['reg_no']
            try:
                student = Student.objects.get(
                                            student_reg_no=reg_no)
            except:
                return HttpResponseRedirect(reverse('students:create', 
                                            args=[reg_no.replace('/','_')]))
            else:
                return HttpResponseRedirect(student.get_absolute_url())
    else:
        if 'next' in request.GET.keys():
            context = {'next': request.GET['next']}
        else:
            context = {}
    return render(request, 'results/reg_no_search.html',context)


def edit_bio_data(request, reg_no):
    """
    This view is supposed to enable the editing of student
    bio data.
    """
    context = {}
    if request.method == 'GET':
        reg_no = reg_no.replace("_", "/")
        if Student.is_valid_reg_no(reg_no):
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                messages.add_message(request, messages.INFO,
                                    '''Student not found. 
                                    Provide student info for registration
                                    ''',
                                    extra_tags='text-info')
                form = StudentBioForm(initial={'student_reg_no':reg_no})
            else:
                form = StudentBioForm(instance=student)
        else:
            messages.add_message(request, messages.ERROR,
                            "Invalid student registration number",
                            extra_tags="text-danger")
            return HttpResponseRedirect(reverse('students:search'))
                        
        if 'next' in request.GET.keys():
            context.update(next=request.GET['next'])
            # print(request.GET['next'])
    
    # process form submission
    if request.method == 'POST':
        if Student.is_valid_reg_no(request.POST['student_reg_no']):
            reg_no = request.POST['student_reg_no']
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                form = StudentBioForm(request.POST, request.FILES)
            else:
                form = StudentBioForm(request.POST, request.FILES, 
                                        instance=student)
            finally:
                if form.is_valid():
                    form.save()
                    if 'next' in request.POST:
                        return HttpResponseRedirect(request.POST['next'])
                    return HttpResponseRedirect(reverse('students:menu'))
        else:
            form = StudentBioForm(request.POST, request.FILES)
            messages.add_message(request, messages.ERROR,
                                    "Invalid student registration number",
                                    extra_tags='text-danger')
    context.update(form=form)
    # print(context)
    return render(request, 'students/bio_data.html', {'form': form})


def update_progress_history(request, reg_no):
    '''This view updates a student's academic progress history.
    '''
    context = {}
    reg_no = reg_no.replace("_", "/")

    if Student.is_valid_reg_no(reg_no):
        try:
            student = Student.objects.get(student_reg_no=reg_no)
        except:
            messages.add_message(request,messages.ERROR,
                                '''No existing record found for student.
                                Provide student info for registration
                                ''',
                                extra_tags="text-danger")
            return HttpResponseRedirect(reverse('students:edit_bio', 
                    args=[reg_no.replace("/","_")])+'?next=%s' %
                    (reverse('students:progress_history',
                                args=[reg_no.replace("/","_")])
                                                )
                    )
        else:
            context.update(student=student)

        if request.method == 'POST':
            form = ProgressHistoryForm(request.POST)
            if form.is_valid():
                form.save()
                try:
                    prog_hist = StudentProgressHistory.objects.get(
                            student_reg_no=request.POST['student_reg_no'],
                            session=int(request.POST['session']))
                except:
                    form = ProgressHistoryForm(request.POST)
                else:
                    form = ProgressHistoryForm(request.POST, instance=student)
                finally:
                    if form.is_valid():
                        form.save()
                        messages.add_message(request, messages.SUCCESS,
                                                    "Progress history saved.",
                                                    extra_tags="text-success")
                    else:
                        print("Form is not valid")
                        messages.add_message(request, messages.SUCCESS,
                                                    "Error. Please check form",
                                                    extra_tags="text-danger")
        existing_progress_history = StudentProgressHistory.objects.all(                
                                        ).filter(student_reg_no=student
                                        ).select_related('session',
                                                        'level_of_study',
                                                        'student_reg_no'
                                        ).order_by('session')
        context.update(existing_progress_history=existing_progress_history)
        context.update(form=ProgressHistoryForm(instance=student))

    return render(request, 'students/progress_history.html', context)

