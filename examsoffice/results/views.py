from django.http import HttpResponse
from django.urls import reverse
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.db.models import (OuterRef, Subquery, Value, Count)
from django.db.models.functions import Concat
import csv
from datetime import date
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
from openpyxl.writer.excel import save_virtual_workbook
from . import models as ex
from results.utils import (student_transcript, 
                            class_result_spreadsheet,
                            collated_results_spreadsheet,
                            class_failure_spreadsheet)

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
            student, _ = ex.Student.objects.get_or_create(student_reg_no=reg_no)
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
        student_info, _ = ex.Student.objects.get_or_create(student_reg_no=reg_no) 
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

        student_info, _ = ex.Student.objects.get_or_create(student_reg_no=reg_no)

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
    context = {'reg_no':reg_no, 'courses':course_qs, 'semesters':semester_qs,
                'valid_grades':_valid_grades}
    
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
            messages.add_message(request, messages.ERROR, 
                        'Course/Semester Mismatch!',extra_tags='text-danger')
    else:
            messages.add_message(request, messages.ERROR, 
                                'Uknown Error, Please Try again')
    return HttpResponseRedirect(student.get_record_creation_url())

@login_required
def recent_results(request):
    queryset = ex.Result.objects.all().select_related('semester', 'course'
                        ).order_by('-id').values(
                            'id','student_reg_no','course_id__course_title',
                             'course_id__course_code',
                            'course_id__course_semester','semester_id__desc',
                            'semester_id__semester','letter_grade')[:20]
    context = {'object_list': queryset}
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

@login_required
def recent_results_bulk(request):
    '''This view will find results for the  last N unique courses
        uploaded to the db.'''
    qs = ex.Result.objects.all().order_by('-id').select_related('course', 
                        'semester')
    course_count = 0
    for idx, entry in enumerate(qs):
        if idx != 0 and qs[idx].course != qs[idx-1].course:
            course_count += 1
        if course_count == 26:
            break
    min_id = qs[idx].id
    final_qs = ex.Result.objects.all().filter(id__gt=min_id).order_by('-id'
                        ).values('course__course_title', 'course__course_code',
                        'semester__desc')
    df = pd.DataFrame(final_qs)
    grouped = df.groupby(['course__course_code', 'semester__desc'], sort=False)
    new_df = grouped.agg(np.size)
    grouped_dict = new_df.to_dict('dict')['course__course_title']
    template = 'results/recent_results_bulk.html'
    return render(request, template, {'qs': grouped_dict})

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
                                                defaults={
                                                'letter_grade': row['grade'].upper()}
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
                error_text = (f'''The following rows in the file contains invalid entries:
                                {sorted(invalid_rows)}''')
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
                            f"{number_of_results} result(s) were deleted",
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
    required_sessions = (request.POST['required_sessions'] 
                                    if request.method == 'POST' else None)
    transcipt_data = {}
    def qs_to_result_df(qs, col_names):
        df = DataFrame(list(qs))
        df.rename(columns={k:v for (k,v) in enumerate(col_names)}, inplace=True)
        
        return df

    if ex.Student.is_valid_reg_no(reg_no):
        required_fields = ['course_id__course_code','course_id__course_title',
                        'course_id__course_level','letter_grade',
                        'semester_id__desc', 'semester_id__session',
                        'course_id__credit_load']

        student = get_object_or_404(ex.Student, student_reg_no=reg_no)
        student_results = ex.Result.objects.filter(student_reg_no=reg_no
                        ).prefetch_related('course', 'semester').values_list(
                            *required_fields)

        student_bio = [student.full_name, reg_no,
                            student.get_level_of_study()]
        transcipt_data['student_bio'] = student_bio
        
        if student_results != None:
            result_sessions = list(student_results.values_list(
                                'semester_id__session', flat=True).distinct())
            selected_sessions = (required_sessions if required_sessions 
                                                        else result_sessions)
            selected_sessions = sorted(result_sessions)
            transcipt_body = {}
            for session in selected_sessions:
                session_entry = {}
                session_res = student_results.filter(
                                                semester_id__session=session)
                first_sem_res = session_res.filter(semester_id__semester=1
                                        ).order_by('course_id__course_level')
                second_sem_res = session_res.filter(semester_id__semester=2
                                        ).order_by('course_id__course_level')
                if len(first_sem_res) > 0:
                    first_sem_df = DataFrame(list(first_sem_res))
                    first_sem_df.rename(columns={k:v for (k,v) in enumerate(required_fields)}, inplace=True)
                    first_sem_df['weight'] = (first_sem_df['course_id__credit_load']
                                                * [5 if x == 'A' else 4 
                                                if x == 'B' else 3 if 
                                                x == 'C' else 2 if x == 'D'
                                                else 1 if x == 'E' else 0 
                                                for x in 
                                                first_sem_df['letter_grade']])
                    session_entry['first'] = first_sem_df
                
                if len(second_sem_res) > 0:
                    second_sem_df = DataFrame(list(second_sem_res))
                    second_sem_df.rename(columns={k:v for (k,v) in enumerate(required_fields)}, inplace=True)
                    second_sem_df['weight'] = (second_sem_df['course_id__credit_load']
                                                * [5 if x == 'A' else 4 
                                                if x == 'B' else 3 if 
                                                x == 'C' else 2 if x == 'D'
                                                else 1 if x == 'E' else 0 
                                                for x in 
                                                second_sem_df['letter_grade']])
                    session_entry['second'] = second_sem_df    
                transcipt_body[session] = session_entry
            transcipt_data['transcript_body'] = transcipt_body
            wb = student_transcript(transcipt_data)

            file_name = f'Academic Transcript of {student.full_name.replace(",","")}.xlsx'
            response = HttpResponse(content=save_virtual_workbook(wb), 
                                    content_type='application/ms-excel')
            response['Content-Disposition']  = f'attachment; filename={file_name}'
            return response
        
        else:
            messages.add_message(request, messages.ERROR, 
                                "No results were found for the student",
                                extra_tags="text-danger")
            return HttpResponseRedirect(reverse('results:transcripts'))

    return render(request, template_name, {})

@login_required
def generic_class_info_handler(request, expected_yr_of_grad, file_name, 
                            spread_sheet_method=class_failure_spreadsheet):

    class_query = ex.Student.objects.all().select_related('mode_of_admission'
                        ).filter(expected_yr_of_grad=expected_yr_of_grad
                        ).values_list(
                        'student_reg_no',
                        'mode_of_admission_id__mode_of_admission'
                        )
    if len(class_query) == 0:
        messages.add_message(request, messages.ERROR, 
                    f'''No students are currently registered with 
                    {expected_yr_of_grad} as their year of graduation''',
                    extra_tags='text-danger')
        return HttpResponseRedirect(reverse('results:spreadsheets'))

    class_reg_no = list(class_query.values_list('student_reg_no', flat=True))
    class_list = []
    for el in class_query:
        name = ex.Student.objects.get(student_reg_no=el[0]).full_name
        class_list.append([el[0], name, el[1]])

    result_qs = ex.Result.objects.all().select_related(
                    'semester', 'course').filter(
                        student_reg_no__in=class_reg_no).values_list(
                        'course_id__course_title', 
                    'course_id__course_code', 'course_id__credit_load', 
                    'course_id__course_level','semester_id__desc',
                     'letter_grade',)
    
    if len(class_list) > 0:        
        wb = spread_sheet_method(result_qs=result_qs, 
                                    class_list=class_list,
                                    expected_yr_of_grad=expected_yr_of_grad)
        response = HttpResponse(content=save_virtual_workbook(wb), 
                                content_type='application/ms-excel')
        response['Content-Disposition']  = f'attachment; filename={file_name}'
        return response
    else:
        messages.add_message(request, messages.ERROR,
                        "No results have been uploaded for students of this level",
                        extra_tags='text-danger')

    return render(request, 'results/class_spreadsheet.html', {})


@login_required
def class_outstanding_courses(request, expected_yr_of_grad):
    file_name = f'Class of {expected_yr_of_grad} Extra Load Summary.xlsx'
    return generic_class_info_handler(request, expected_yr_of_grad, file_name)

@login_required
def class_speadsheet_generator(request, expected_yr_of_grad):
    file_name = f'Class of {expected_yr_of_grad} Results.xlsx'
    return generic_class_info_handler(request, expected_yr_of_grad, file_name,
                                spread_sheet_method=class_result_spreadsheet)

def result_collation(request, session, level):
    '''This view will take two args: level of study and session.
        Using these, it will produce a file response (excel worksheet) of all 
        available results for the given session and level of study '''
    
    session = session.replace("_", "/")
    try:
        level_of_study = int(level)
    except ValueError:
        return HttpResponseBadRequest("Invalid Arg(s) provided")
    # session_obj = ex.Session
    student_info = ex.Student.objects.filter(student_reg_no=OuterRef('student_reg_no'))
    qs = ex.Result.objects.all().select_related('course', 'semester'
                ).filter(semester__session=session,course__course_level=level_of_study).annotate(
                    name=Concat(Subquery(student_info.values('last_name')), Value(' '),
                            Subquery(student_info.values('first_name')),Value(' '),
                            Subquery(student_info.values('other_names')))
                ).order_by('course__course_semester')
    result_dict = {}
    if len(qs)>0:
        for idx, el in enumerate(qs):
            result_dict[(idx)] = {
                        'reg_no': el.student_reg_no,
                        'name': el.name,
                        'course_title': el.course.course_title,
                        'course_code': el.course.course_code,
                        'semester': el.course.course_semester.semester,
                        'grade': el.letter_grade
                        }
        result_df = DataFrame(result_dict)
        result_df = result_df.transpose()
        wb = collated_results_spreadsheet(result_df)
        file_name = f'{session} Collated Results - {int(level) * 100}L.xlsx'
        response = HttpResponse(content=save_virtual_workbook(wb), 
                                content_type='application/ms-excel')
        response['Content-Disposition']  = f'attachment; filename={file_name}'
        return response
    else:
        messages.add_message(request, messages.ERROR, 
        "No results found for the selected session/level of study")
        return HttpResponseRedirect(reverse('results:collation'))

@login_required
def result_collation_form(request):
    template = 'results/result_collation_form.html'
    context = {}
    if request.method == 'GET':
        sessions = ex.Session.objects.all().order_by('-session')
        levels_of_study = [x for x in range(1, 6)]
        context = {'sessions':sessions, 'levels_of_study':levels_of_study}

    else:
        if request.POST['session'] and request.POST['level']:
            session = request.POST['session'].replace('/','_')
            level = request.POST['level']
            next_url = reverse('results:result_collation', 
                kwargs={'session':session,'level':level})

            return HttpResponseRedirect(
                        reverse('index:download_info')+'?next=%s' % next_url)
        else:
            messages.add_message(request, messages.ERROR,
                                "Please verify information provided is valid",
                                extra_tags="text-danger")
    return render(request, template, context)

@login_required
def result_spreadsheet_form(request):
    template = 'results/spreadsheet_form.html'
    context = {}

    if request.method == 'GET':
        expected_yrs_of_grad = sorted(
                [x for x in range(2017, (date.today().year+5))],reverse=True)
        context = {'expected_yrs_of_grad': expected_yrs_of_grad}
        return render(request, template, context)
    else:
        if request.POST['expected_yr_of_grad']:
            print('got here')
            try:
                expected_yr_of_grad = int(request.POST['expected_yr_of_grad'])
            except ValueError:
                return HttpResponseBadRequest(
                                    "Invalid Session. Select a valid year.")
            else:
                next_url = reverse('results:generate_class_spreadsheet', 
                        kwargs={'expected_yr_of_grad': expected_yr_of_grad})
                return HttpResponseRedirect(
                        reverse('index:download_info')+'?next=%s' % next_url)

@login_required
def class_outstanding_courses_form(request):
    template = 'results/spreadsheet_form.html'
    context = {}

    if request.method == 'GET':
        expected_yrs_of_grad = sorted(
                [x for x in range(2017, (date.today().year+5))],reverse=True)
        context = {'expected_yrs_of_grad': expected_yrs_of_grad}

    elif request.method == 'POST':
        if request.POST['expected_yr_of_grad']:
            try:
                expected_yr_of_grad = int(request.POST['expected_yr_of_grad'])
            except ValueError:
                return HttpResponseBadRequest(
                                    "Invalid Session. Select a valid year.")
            else:
                next_url = reverse('results:class_outstanding_courses', 
                        kwargs={'expected_yr_of_grad': expected_yr_of_grad})
                return HttpResponseRedirect(
                        reverse('index:download_info')+'?next=%s' % next_url)
    return render(request, template, context)

@login_required
def student_transcript_form(request):
    template = 'results/reg_no_search.html'

    if request.method == 'POST':
        reg_no = request.POST['reg_no'] or None
        if ex.Student.is_valid_reg_no(reg_no):
            next_url = reverse('results:generate_transcript', 
                        kwargs={'reg_no': reg_no.replace("/", "_")})
            return HttpResponseRedirect(
                        reverse('results:transcript_download_info',
                        kwargs={'reg_no': reg_no.replace('/','_')}
                        )+'?next=%s' % next_url)
        else:
            messages.add_message(request, messages.ERROR,
                                'Invalid Student Registration Number',
                                extra_tags='text-danger')
    return render(request, template, {})

@login_required
def transcript_download_info(request, reg_no):
    template = 'results/transcript_download_info.html'
    context = {}
    if request.method == 'GET':
        try:
            context.update(next=request.GET['next'])
        except:
            pass
    reg_no = reg_no.replace("_", "/")
    if ex.Student.is_valid_reg_no(reg_no):
        student = get_object_or_404(ex.Student, student_reg_no=reg_no)
        hod_info = get_object_or_404(ex.Lecturer, head_of_dept=True)
        context.update(student=student, hod=hod_info)
    else:
        messages.add_message(request, messages.ERROR, 
                            "Invalid Student Registration Number",
                            extra_tags='text-danger')
        HttpResponseRedirect(reverse('results:transcripts'))
    return render(request, template, context)
