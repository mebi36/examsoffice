from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (
    results_menu, edit_result, result_modify, student_search_processor,
    find_student, student_records, add_result, result_add_processor,
    rogue_results, delete_result, result_upload_options, upload_result_file,
    delete_by_session, student_transcript_generator, class_speadsheet_generator,

    student_records_partial, delete_student_result
)
app_name = 'results'

urlpatterns = [
    path('',results_menu, name='results_menu'),
    # path('editable/', views.EditResultsView.as_view(),name='editable_results'),
    path('editresult/<int:pk>/', edit_result, name='result_edit'),
    path('modify/<int:pk>/', result_modify, name='modify'),
    path('searchresults/',student_search_processor,name='student_search_results' ),
    path('search/', find_student, name='student_search'),
    path('records/<str:reg_no>/',student_records, name='student_records'),
    path('add/<str:reg_no>/', add_result, name='add'),
    path('result_add/', result_add_processor, name='add_processor'),
    path('recent/',rogue_results,name='recent_results'),
    path('delete/<int:pk>',delete_result,name='delete'),
    path('upload/', result_upload_options, name='upload'),
    path('upload file/', upload_result_file, name='upload_result_file'),
    path('delete by session/', delete_by_session, name='delete_by_session'),
    path('transcript/<str:reg_no>/',student_transcript_generator, name='generate_transcript'),
    path('spreadsheet/<str:expected_yr_of_grad>/',class_speadsheet_generator, name='generate_class_spreadsheet'),

    path('hx/records/<str:reg_no>/', student_records_partial, name='student_records_partial'),
    path('hx/delete/<int:pk>',delete_student_result,name='delete_student_result'),
]