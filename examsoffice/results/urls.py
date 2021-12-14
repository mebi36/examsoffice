from django.urls.conf import path
from django.urls.resolvers import URLPattern

from .views import (
    possible_graduands_form, result_collation, results_menu, edit_result, student_search_processor,
    find_student, student_records, add_result, result_add_processor,
    recent_results, recent_results_bulk, delete_result, result_upload_options, upload_result_file,
    delete_by_session, student_transcript_generator, class_speadsheet_generator,
    result_collation_form, result_spreadsheet_form, student_transcript_form,
    transcript_download_info, class_outstanding_courses, class_outstanding_courses_form,all_results_agg,
    possible_graduands,

    delete_student_result
)
app_name = 'results'

urlpatterns = [
    path('',results_menu, name='menu'),
    path('editresult/<int:pk>/', edit_result, name='result_edit'),
    path('searchresults/',student_search_processor,name='student_search_results' ),
    path('search/', find_student, name='student_search'),
    path('records/<str:reg_no>/',student_records, name='student_records'),
    path('add/<str:reg_no>/', add_result, name='add'),
    path('result_add/', result_add_processor, name='add_processor'),
    path('all/', all_results_agg, name='all'),
    path('recent uploads', recent_results_bulk, name='recent_uploads'),
    path('recent/',recent_results,name='recent'),
    path('delete/<int:pk>',delete_result,name='delete'),
    path('upload/', result_upload_options, name='upload'),
    path('upload file/', upload_result_file, name='upload_result_file'),
    path('delete by session/', delete_by_session, name='delete_by_session'),
    path('transcripts/',student_transcript_form, name='transcripts'),
    path('transcript download/<str:reg_no>',transcript_download_info, name='transcript_download_info'),
    path('transcript/<str:reg_no>/',student_transcript_generator, name='generate_transcript'),
    path('spreadsheets/', result_spreadsheet_form, name='spreadsheets'),
    path('spreadsheet/<str:expected_yr_of_grad>/',class_speadsheet_generator, name='generate_class_spreadsheet'),
    path('outstanding courses/class/', class_outstanding_courses_form, name='class_outstanding_courses'),
    path('outstanding courses/class/<str:expected_yr_of_grad>/', class_outstanding_courses, name='class_outstanding_courses'),
    path('collation/', result_collation_form, name='collation'),
    path('result_collation/session=<str:session>/level=<str:level>', result_collation,name='result_collation'),
    path('hx/delete/<int:pk>',delete_student_result,name='delete_student_result'),
    path('possible graduands/', possible_graduands_form, name='possible_graduands_form'),
    path('possible graduands/<str:expected_yr_of_grad>', possible_graduands, name='possible_graduands'),
]