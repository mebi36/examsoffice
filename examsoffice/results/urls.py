"""URL patterns for the results app."""

from django.urls.conf import path
from django.urls.resolvers import URLPattern

from results import views

app_name = "results"

urlpatterns = [
    path("editresult/<int:pk>/", views.edit_result, name="result_edit"),
    path(
        "searchresults/",
        views.student_search_processor,
        name="student_search_results",
    ),
    path("search/", views.find_student, name="student_search"),
    path("records/<str:reg_no>/", views.student_records, name="student_records"),
    path("add/<str:reg_no>/", views.add_result, name="add"),
    path("result_add/", views.result_add_processor, name="add_processor"),
    path("all/", views.all_results_agg, name="all"),
    path("recent uploads", views.recent_results_bulk, name="recent_uploads"),
    path("recent/", views.recent_results, name="recent"),
    path("delete/<int:pk>", views.delete_result, name="delete"),
    path("upload/", views.result_upload_options, name="upload"),
    path("upload file/", views.upload_result_file, name="upload_result_file"),
    path("delete by session/", views.delete_by_session, name="delete_by_session"),
    path("transcripts/", views.student_transcript_form, name="transcripts"),
    path(
        "transcript download/<str:reg_no>",
        views.transcript_download_info,
        name="transcript_download_info",
    ),
    path(
        "transcript/<str:reg_no>/",
        views.student_transcript_generator,
        name="generate_transcript",
    ),
    path("spreadsheets/", views.result_spreadsheet_form, name="spreadsheets"),
    path(
        "spreadsheet/<str:expected_yr_of_grad>/",
        views.class_speadsheet_generator,
        name="generate_class_spreadsheet",
    ),
    path(
        "outstanding courses/class/",
        views.class_outstanding_courses_form,
        name="class_outstanding_courses",
    ),
    path(
        "outstanding courses/class/<str:expected_yr_of_grad>/",
        views.class_outstanding_courses,
        name="class_outstanding_courses",
    ),
    path("collation/", views.result_collation_form, name="collation"),
    path(
        "result_collation/session=<str:session>/level=<str:level>",
        views.result_collation,
        name="result_collation",
    ),
    path(
        "hx/delete/<int:pk>",
        views.delete_student_result,
        name="delete_student_result",
    ),
    path(
        "possible graduands/",
        views.possible_graduands_form,
        name="possible_graduands_form",
    ),
    path(
        "possible graduands/<str:expected_yr_of_grad>",
        views.possible_graduands,
        name="possible_graduands",
    ),
]
