from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView

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
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                messages.add_message(request, messages.INFO,
                                    '''No student bio data found. 
                                    Please provide student details.''',
                                    extra_tags='text-primary')
                return HttpResponseRedirect(reverse('students:create_bio', 
                                    kwargs={'reg_no':reg_no.replace('/','_')}))
            else:
                return HttpResponseRedirect(student.get_absolute_url())
    else:
        if 'next' in request.GET.keys():
            context = {'next': request.GET['next']}
        else:
            context = {}
    return render(request, 'results/reg_no_search.html',context)

@never_cache
def edit_bio_data(request, reg_no):
    """
    This view is supposed to enable the editing of student
    bio data.
    """
    context = {}
    reg_no = reg_no.replace("_", "/")
    if request.method == 'GET':
        if Student.is_valid_reg_no(reg_no):
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                messages.add_message(request, messages.INFO,
                                    '''Student not found. 
                                    Provide student info for registration
                                    ''',
                                    extra_tags='text-info')
                return HttpResponseRedirect(reverse('students:create_bio',
                                    kwargs={'reg_no':reg_no.replace("/","_")}))
            else:           
                form = StudentBioForm(instance=student)
                context['reg_no'] = reg_no
                context['form'] = form
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
        if Student.is_valid_reg_no(reg_no):
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                # form = StudentBioForm(request.POST, request.FILES) if len(request.FILES)==0 else StudentBioForm(request.POST)
                print("an exception occured")
            else:
                # form = StudentBioForm(request.POST, request.FILES, 
                #                         instance=student) if request.FILES is not None else StudentBioForm(request.POST, instance=student)
                form = StudentBioForm(request.POST, instance=student)
                initial_obj_state = StudentBioForm(instance=student)
            finally:
                if form.is_valid():
                    # try:
                    #     form.save()
                    # except:
                    #     messages.add_message(request, messages.ERROR,
                    #                     "Fatal error",extra_tags='bg-danger')
                    #     return HttpResponseRedirect(reverse('students:search'))
                    # else:    
                    #     messages.add_message(request, messages.SUCCESS,
                    #                     "Save successful",
                    #                     extra_tags='text-success')
                    # form.save()
                    for field in form.fields:
                        print(student.pk, field, 'then ', form[field].value())
                        if form[field].value() not in [None, ''] and form[field].value() != initial_obj_state[field].value():
                            Student.objects.get(student_reg_no=reg_no).field = form[field].value()
                            print(f"after {field}\n\n\n\n\n\n\n")
                            student.save()
                    if 'next' in request.POST:
                        return HttpResponseRedirect(request.POST['next'])
                    return HttpResponseRedirect(reverse('students:search'))
        else:
            form = StudentBioForm(request.POST, request.FILES)
            messages.add_message(request, messages.ERROR,
                                    "Invalid student registration number",
                                    extra_tags='text-danger')
    context.update(form=form)
    # print(context)
    return render(request, 'students/bio_data.html',context)


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

def create_bio_data(request, reg_no):

    '''This view updates a student's academic progress history.'''
    context = {}
    reg_no = reg_no.replace("_", "/")
    template = 'students/bio_data.html'
    form = StudentBioForm(initial={'student_reg_no':reg_no})
    if request.method == 'GET':
        try:
            Student.objects.get(student_reg_no=reg_no)
        except:
            context = {'form': form}
            return render(request, template, context)
        else:
            messages.add_message(request, messages.INFO, 
                                "Student Bio Records Already Exists",
                                extra_tags='text-primary')
            return HttpResponseRedirect(reverse('students:edit_bio',
                                        kwargs={'reg_no':reg_no.replace('/','_')}))
    elif request.method == 'POST':
        if Student.is_valid_reg_no(reg_no):
            student = Student(student_reg_no=reg_no)
            student.save()

            for field in form.fields:
                if form[field].value() not in [None, '', 'student_reg_no']:
                    Student.objects.get(student_reg_no=reg_no).field = form[field].value()
                    student.save()
            messages.add_message(request, messages.SUCCESS, 
                                "Student bio data saved",
                                extra_tags='text-success')
        else:
            messages.add_message(request, messages.ERROR, 
                                "Registration Number is invalid",
                                extra_tags='text-danger')
        return HttpResponseRedirect(reverse('students:search'))
        
# class StudentUpdateView(UpdateView):
#     model = Student
#     fields = ['student_reg_no', 'last_name', 'first_name', 'other_names', 'email',
#                 'phone_number', 'sex', 'marital_status', 'date_of_birth', 
#                 'town_of_origin', 'lga_of_origin', 'state_of_origin', 'nationality',
#                 'mode_of_admission', 'level_admitted_to', 'mode_of_study',
#                 'year_of_admission', 'expected_yr_of_grad', 'graduated', 'address_line1',
#                 'address_line2', 'city', 'state', 'country', 'class_rep', 'current_level_of_study', 'cgpa']
#     template_name = 'students/student_update_form.html'
#     form = StudentBioForm

