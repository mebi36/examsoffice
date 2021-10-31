from django.http import response, HttpResponse
from django.urls import reverse
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.decorators.cache import never_cache
import re
import csv
import os
import pandas as pd

from . import models as ex
from django.db.models.functions import Coalesce
from . import utils
#Generating querysets that will be used often in many views of this app
_queryset = ex.Result.objects.all().select_related('course',                                           
                                'semester').values(
                                    'id',
                                    'course_id__course_title',
                                    'course_id__course_semester',
                                    'course_id__course_code',
                                    'course_id__credit_load',
                                    'semester_id__desc', 'letter_grade',
                                    'semester_id__id',
                                    'student_reg_no')

_valid_grades = ['A', 'B', 'C', 'D', 'E', 'F']


# # @login_required
# class EditResultsView(generic.ListView):
#     template_name = "results/edit_results_view.html"
#     context_object_name = 'result'
#     queryset = _queryset

def results_menu(request):
    """A view to display all the actions a user can perform
        with regards to student results"""
    
    return render(request, 'results/menu.html', {})

@login_required
def edit_result(request, pk):
    if request.method == 'POST':
        result_details = get_object_or_404(ex.Result, id=pk)
        if (request.POST['grade'].upper() in _valid_grades and
                request.POST['grade'].upper() != result_details.letter_grade):
            result_details.letter_grade = request.POST['grade'].upper()
            result_details.save()
            messages.add_message(request, messages.SUCCESS,
                                    "Update successful",
                                    extra_tags="text-success")

    queryset = _queryset
    result_details = get_object_or_404(queryset, id=pk)
    context = { 'result': result_details }
    
    return render(request,'results/edit_result.html',context)

@login_required
def find_student(request):
    """A view that renders a form for users to search for a
        student's academic record with his/her registration number
        
        view could also be modified to process searching 
        for a student's record given just his/her name"""

    template_name = 'results/reg_no_search.html'
    if request.method == 'POST':
        reg_no = request.POST['reg_no']
        if ex.Student.is_valid_reg_no(reg_no):
            student = ex.Student.objects.get_or_create(student_reg_no=reg_no)
            student = ex.Student.objects.get(student_reg_no=reg_no)
            return HttpResponseRedirect(student.get_records_url())
        else:
            messages.add_message(request, messages.ERROR, 
                                    "Invalid Registration Number",
                                    extra_tags='text-danger')
    return render(request, template_name, {})


@login_required
def student_search_processor(request, reg_no):
    template_name = "results/student_records.html"
    reg_no = request.POST['reg_no']
    if ex.Student.is_valid_reg_no(reg_no):
        object_list =  _queryset.filter(student_reg_no = reg_no)
        student_info = ex.Student.objects.get_or_create(student_reg_no=reg_no) 
        student_info = ex.Student.objects.get(student_reg_no=reg_no)
        context = {'object_list': object_list, 'student': student_info}
    
        return render(request, template_name, context)


@login_required
def student_records(request, reg_no):
    template_name = 'results/student_records.html'
    reg_no = reg_no.replace("_", "/")

    if ex.Student.is_valid_reg_no(reg_no):
        queryset = ex.Result.objects.all().filter(student_reg_no=reg_no
                            ).select_related('course','semester')
    
        if len(queryset) < 1:
            messages.add_message(request, messages.INFO, 
                                '''No academic records were found for the 
                                    registration number entered.''',
                                        extra_tags='text-danger')

        if not ex.Student.objects.get(student_reg_no=reg_no):
            ex.Student.objects.create(student_reg_no=reg_no)
    
        student_info = ex.Student.objects.get(student_reg_no=reg_no)

        context = {'object_list': queryset, 'student': student_info,}
    else:
        messages.add_message(request, messages.ERROR, 
                                '''Invalid Student Registration Number''',
                                    extra_tags='text-danger')
        context = {}

    return render(request, template_name, context)

@login_required
def add_result(request, reg_no):
    """A view that renders a form for users to add a result for a particular
        student"""
    reg_no = reg_no.replace("_", "/")
    course_qs = ex.Course.objects.all()
    semester_qs = ex.SemesterSession.objects.all().order_by('-session')
    context = {'reg_no': reg_no, 'courses': course_qs, 'semesters': semester_qs,
                'valid_grades': _valid_grades}
    
    return render(request, 'results/add_result.html', context)

@login_required
def result_add_processor(request): 
    student = ex.Student.objects.get(request.POST['reg_no'])
    if (request.POST['semester'] != None 
                    and request.POST['course'] != '' 
                    and request.POST['grade'].upper() in _valid_grades):
        course = ex.Course.objects.get(id=int(request.POST['course']))
        semester = ex.SemesterSession.objects.get(
                                id=int(request.POST['semester']))
        if course.course_semester == semester.semester:
            result_details = ex.Result.objects.create(
                    student_reg_no=request.POST['reg_no'],
                    course=course,
                    semester=semester,
                    letter_grade=request.POST['grade'],
                                                )
            result_details.save()
    
            return HttpResponseRedirect(student.get_records_url())
        else:
            messages.add_message(request, messages.ERROR, 'Course/Semester Mismatch!',
                                    extra_tags='text-danger')
    else:
            messages.add_message(request, messages.ERROR, 
                                'Uknown Error, Please Try again')
    return HttpResponseRedirect(student.get_record_creation_url())

@login_required
def recent_results(request):
    queryset = _queryset.order_by('-id')[:100]
    
    context = {'object_list': queryset}
    template = 'results/recent_results.html'

    return render(request, template, context)

@login_required
def rogue_results(request):
    queryset = ex.Result.objects.all().select_related('semester', 'course'
                        ).order_by('-id').values(
                            'id','student_reg_no','course_id__course_title',
                             'course_id__course_code',
                            'course_id__course_semester','semester_id__desc',
                            'semester_id__semester','letter_grade')[:20]
    context = {'object_list': queryset}
    print(queryset)
    if request.htmx:
        template = 'results/partials/rogue_results.html'
    else:
        template = 'results/rogue_results.html'

    return render(request, template, context)

@login_required
def delete_result(request, pk):
    result_details = get_object_or_404(ex.Result, id=pk)
    if result_details:
        ex.Result.objects.get(id=pk).delete()

    return HttpResponseRedirect(reverse('results:recent_results'))

@login_required
def delete_student_result(request, pk):
    result_details = get_object_or_404(ex.Result, id=pk)
    if result_details:
        student = ex.Student.objects.get(
                            student_reg_no=result_details.student_reg_no)
        ex.Result.objects.get(id=pk).delete()
        

    return HttpResponseRedirect(student.get_records_url())


"""For bulk result operations like:
    class result uploads
    deletion of entire results for a particular session
"""

@login_required
def result_upload_options(request):
    RESULT_UPLOAD_OPTIONS = ('Upload results without scores', 
                             'Upload results with scores',)
    template_name = 'results/result_upload_format.html'
    context = {'upload_options': RESULT_UPLOAD_OPTIONS}
    if request.method == 'POST':
        response = HttpResponse(
               content_type='text/csv',
               headers={'Content-Disposition': 'attachment; filename="resultformat.csv"'},
           ) 
        writer = csv.writer(response)
        if request.POST['upload_option'] == 'Upload results without scores':
           writer.writerow(['Student Registration Number', 'Grade'])
        elif request.POST['upload_option'] == 'Upload results with scores':
            writer.writerow(['Student Registration Number', 'CA Score', 
                             'Exam Score','Grade'])
        else:
            messages.add_message(request, messages.ERROR, 
                                "Something went wrong. Please try again",
                                extra_tags="text-danger")
            return HttpResponseRedirect(reverse('results:upload'))
        return response

    return render(request, template_name, context)

@login_required
@never_cache
def upload_result_file(request):
    template_name = 'results/upload_result_file.html'
    course_qs = ex.Course.objects.all()
    semester_qs = ex.SemesterSession.objects.all().order_by('-session')
    context = {'courses': course_qs, 'semesters': semester_qs}
    if request.method == 'POST' and request.FILES:
        # begin by checking if uploaded file is a csv file
        try:
            df = pd.read_csv(request.FILES['result_file'], skipinitialspace=True)
            #you can define a chunksize parameter in the read_csv method
            # to handle large file sizes [chunksize=1000]
        except:
            messages.add_message(request, messages.ERROR, 
                                "Invalid File. File must be a non-empty CSV file.",
                                extra_tags="text-danger")
            return HttpResponseRedirect(reverse('results:upload_result_file'))
        else:
            invalid_result_index_list = []
            # strip whitespaces from dataframe
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            # append result entries w empty reg no/grade to invalid result index list
            invalid_result_index_list = df[df.isna().any(axis=1)].index.values.tolist()
            
            original_df = df.copy() #make a copy of dataframe before modification
            
            # remove rows with empty entry for any required column
            df.dropna(axis=0,inplace=True)
            if len(df) > 0:
                if len(df.columns) == 2 and (
                    list(df.columns)[0] == 'Student Registration Number'and
                    list(df.columns)[1] == 'Grade'):
                    df.rename(columns={'Student Registration Number': 'reg_no',
                                        'Grade': 'grade'}, inplace=True)
                    for index, row in df.iterrows():
                        if row['grade'].upper() in _valid_grades: 
                            if ex.Student.is_valid_reg_no(row['reg_no']):
                                course = ex.Course.objects.get(
                                            id=int(request.POST['course']))
                                semester = ex.SemesterSession.objects.get(
                                                    id=int(request.POST['semester']))
                                result_details = ex.Result.objects.update_or_create(
                                                    student_reg_no=row['reg_no'],
                                                    course=course,
                                                    semester=semester,
                                                    defaults={'letter_grade': row['grade'].upper()}
                                                    )

                            else:
                                invalid_result_index_list = (invalid_result_index_list +
                                    original_df.index[original_df['Student Registration Number']==row['reg_no']].tolist())
                        else:
                            invalid_result_index_list.append(
                                original_df.index[original_df['Grade']==row['grade']].tolist())
                    
                elif len(df.columns) == 4 and (
                    list(df.columns)[0] == 'Student Registration Number'and
                    list(df.columns)[1] == 'CA Score' and
                    list(df.columns)[2] == 'Exam Score' and
                    list(df.columns)[3] == 'Grade'):
                    df.rename(columns={'Student Registration Number': 'reg_no',
                                        'CA Score': 'ca_score',
                                        'Exam Score': 'exam_score',
                                        'Grade': 'grade'}, inplace=True)
                    for index, row in df.iterrows():
                        if isinstance(row['ca_score'], (int, float)):
                            if isinstance(row['exam_score'], (int, float)):
                                if row['grade'].upper() in _valid_grades:
                                    if ex.Student.is_valid_reg_no(row['reg_no']):
                                        course = ex.Course.objects.get(
                                                    id=int(request.POST['course']))
                                        semester = ex.SemesterSession.objects.get(
                                                            semester_number=int(request.POST['semester']))
                                        result_details = ex.Result.objects.update_or_create(
                                                            student_reg_no=row['reg_no'],
                                                            course=course,
                                                            semester=semester,
                                                            defaults={'letter_grade': row['grade'].upper(),
                                                                    'ca_score': row['ca_score'],
                                                                    'exam_score': row['exam_score']}
                                                            )
                                else:
                                    invalid_result_index_list.append(
                                original_df.index[original_df['Grade']==row['grade']].tolist())
                            else:
                                invalid_result_index_list = (invalid_result_index_list +
                                    original_df.index[original_df['Exam Score'] == row['exam_score']].tolist())
                        else:
                            invalid_result_index_list = (invalid_result_index_list +
                                original_df.index[original_df['CA Score'] == row['ca_score']].tolist())
                else:
                    messages.add_message(request, messages.ERROR, 
                                '''File does not comply with provided format. 
                                Please download and use a valid format.''',
                                extra_tags="text-danger")    
                    return HttpResponseRedirect(reverse('results:upload_result_file'))

            else:
                messages.add_message(request, messages.ERROR, 
                            "Error. File may be missing either column headers or result entries",
                            extra_tags="text-danger")    
                return HttpResponseRedirect(reverse('results:upload_result_file'))

            if len(invalid_result_index_list) == 0:
                messages.add_message(request, messages.SUCCESS,
                                "Result upload successful",
                                extra_tags="text-success")
            else:
                invalid_rows=[]
                for row in invalid_result_index_list:
                    if row not in invalid_rows:
                        invalid_rows.append(row + 2)
                error_text = ('''The following rows in the file contains invalid entries:
                                {}'''.format(sorted(invalid_rows)))
                messages.add_message(request, messages.ERROR,
                                error_text,
                                extra_tags="text-danger")
            return HttpResponseRedirect(reverse('results:upload_result_file'))

    return render(request, template_name, context)   

@login_required
def delete_by_session(request):
    template_name = 'results/delete_by_session.html'
    course_qs = ex.Course.objects.all()
    semester_qs = ex.SemesterSession.objects.all().order_by('-semester')
    context = {'courses': course_qs, 'semesters': semester_qs}

    if request.method == 'POST':
        course = ex.Course.objects.get(
                                        id=int(request.POST['course']))
        semester = ex.SemesterSession.objects.get(id=int(request.POST['semester']))
        if course.course_semester == semester.id:
            queryset = ex.Result.objects.all().filter(
                                                        course=course,
                                                        semester=semester)
            number_of_results = len(queryset)
            if number_of_results > 0:
                ex.Result.objects.filter(course=course,
                                                semester=semester).delete()
                messages.add_message(request, messages.SUCCESS,
                            "{} result(s) were deleted".format(number_of_results),
                            extra_tags="text-success")
            else:
                messages.add_message(request, messages.WARNING,
                            "No results were found for course for the selected session",
                            extra_tags="text-warning")
        else:
            messages.add_message(request, messages.ERROR,
                            "Course is not allocated to selected semester",
                            extra_tags="text-danger")
    return render(request, template_name, context)

@login_required
def student_transcript_generator(request, reg_no):
    template_name = 'results/transcript.html'
    reg_no = reg_no.replace('_','/')
    # if request.method == 'POST':
    required_fields = ['course_id__course_code','course_id__course_title',
                    'course_id__course_level','letter_grade',
                    'semester_number__desc']
    student = get_object_or_404(ex.Student, student_reg_no=reg_no)
    student_results = ex.Result.objects.filter(
                    student_reg_no=reg_no).prefetch_related(
                                'course','semester_number').values(
                                    'course_id__course_code','course_id__course_title',
                                    'course_id__course_level','course_id__credit_load','letter_grade',
                                    'semester_number__desc','semester_number'
                                )
    if student_results != None:
        # # result_df = pd.DataFrame.from_records(student_results.values().order_by('semester_number__desc'))
        result_semesters = list(student_results.values_list('semester_number', flat=True).distinct())
        result_semesters = sorted(result_semesters)

        for semester in result_semesters:
            print(student_results.values_list('semester_number__desc','course_id__course_code','course_id__course_title',
                                'course_id__credit_load','letter_grade').filter(semester_number=semester))
            print('semester ends\n\n')
        #     print(student_results.filter(semester_number=semester).values())
        #     # print(result_df)
        # # hod_name = request.POST['hod_name']
        # # print(result_df)
    return render(request, template_name, {})

@login_required
def class_speadsheet_generator(request, expected_yr_of_grad):
    class_list = ex.Student.objects.all().select_related('mode_of_admission').filter(
                                    expected_year_of_graduation=expected_yr_of_grad).values_list(
                                        'student_reg_no','last_name', 'first_name',
                                        'other_names','mode_of_admission_id__mode_of_admission')
    class_reg_no = list(class_list.values_list('student_reg_no', flat=True))
    class_list = list(class_list)
    result_qs = ex.Result.objects.all().select_related(
                    'semester', 'course').filter(
                        student_reg_no__in=class_reg_no).values_list(
                        'course_id__course_title', 
                    'course_id__course_code', 'course_id__credit_load', 
                    'course_id__course_level','semester_id__desc',
                     'letter_grade',)
    if len(class_list) > 0:
        # wb = opeWorkBook()
        # ws = wb.active()
        # ws.rename('Class of {} Results'.format(expected_yr_of_grad))           
        for student in class_list:
            student_qs = result_qs.filter(student_reg_no=student[0]).order_by('semester')
            if len(student_qs) > 0:
                df = pd.DataFrame.from_records(student_qs)
                df = df.rename(columns = {0: 'course_title', 1: 'course_code', 2: 'credit_load',
                                            3: 'course_level', 4: 'semester', 5: 'grade'})
                df['weight'] = df['credit_load'] * [5 if x == 'A' else 4 
                                                    if x == 'B' else 3 if 
                                                    x == 'C' else 2 if x == 'D'
                                                    else 1 if x == 'E' else 0 
                                                    for x in df['grade']]
                
                print(df)

    return render(request, 'results/class_spreadsheet.html', {})