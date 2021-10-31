from django.shortcuts import render
from django.contrib import messages

from .forms import StudentBioForm
from results.models import Student

# Create your views here.
def students_menu(request):
    transcript_name = 'students/menu.html'

    return render(request, transcript_name, {})

#To-do list:
# finish refactoring code to ensure edit_result logic is working correctly
# 1.    make view for updating individual student bio data: see what forms have to offer for this req
#2.     make view for updating individual student progress history
# 3.    make view for updating entire class bio data
# 4.    make view for updating entire class academic progress history
# 5.    make view for updating the 'current_level_of_study' field for a list of
        # students
# 6.    make app/view for updating the department's current program requirements

# IN the courses app
# 1. Course creation should be possible (only after a rigorous search of the 
#       courses database)
# 2.Make it clear that courses should never be edited due to change in curriculum
    # that rather, new courses have to be created to fit new academic requirements

def edit_bio_data(request, reg_no):
    """
    This view is supposed to enable the editing of student
    bio data. It will get the student's reg number as a kwarg
    in the urlpattern. It will then load a pre-populated model form 
    with existing bio data for student. 
    It will also process any changes and save them back to the db table
    """
    reg_no = reg_no.replace("_", "/")
    if Student.is_valid_reg_no(reg_no):
        student = Student.objects.get(student_reg_no=reg_no)
    
        if request.method == 'POST':
            form = StudentBioForm(request.POST)
        else:
            form = StudentBioForm(instance=student)
            print(form.__dict__)
    else:
        form = StudentBioForm()
        messages.add_message(request, messages.ERROR, 
                            "Invalid Registration Number",
                            extra_tags="text-danger")
    return render(request, 'students/bio_data.html', {'form': form})