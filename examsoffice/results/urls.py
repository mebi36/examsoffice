from django.urls.conf import path
from django.urls.resolvers import URLPattern
from . import views
app_name = 'results'

urlpatterns = [
    path('',views.results_menu, name='results_menu'),
    path('editable/', views.EditResultsView.as_view(),name='editable_results'),
    path('editresult/<int:pk>/', views.edit_result, name='result_edit'),
    path('modify/<int:pk>/', views.result_modify, name='modify'),
    path('searchresults/',views.student_search_processor,name='student_search_results' ),
    path('search/', views.find_student, name='student_search'),
    path('records/<str:reg_no>/',views.student_records, name='student_records'),
    path('add/<str:reg_no>/', views.add_result, name='add'),
    path('result_add/', views.result_add_processor, name='add_processor'),
    path('recent/',views.rogue_results,name='recent_results'),
    path('delete/<int:pk>',views.delete_result,name='delete'),
    path('upload/', views.result_upload_options, name='upload'),
    path('upload file/', views.upload_result_file, name='upload_result_file'),
    path('delete by session/', views.delete_by_session, name='delete_by_session'),
    path('transcript/<str:reg_no>/',views.student_transcript_generator, name='generate_transcript'),
    path('spreadsheet/<str:expected_yr_of_grad>/',views.class_speadsheet_generator, name='generate_class_spreadsheet'),

    path('hx/records/<str:reg_no>/', views.student_records_partial, name='student_records_partial'),
    path('hx/delete/<int:pk>',views.delete_student_result,name='delete_student_result'),
]