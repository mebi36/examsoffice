"""URL patterns for the results app."""

from django.urls.conf import path

from results import views

app_name = "results"

urlpatterns = [
    path("edit/<int:pk>/", views.ResultObjectUpdateView.as_view(), name="edit"),
    path(
        "detail/<int:pk>/",
        views.ResultObjectDetailView.as_view(),
        name="detail",
    ),
    path(
        "student/<str:reg_no>/",
        views.StudentAcademicRecordsListView.as_view(),
        name="student-records",
    ),
    path("add/<str:reg_no>/", views.ResultCreateView.as_view(), name="add"),
    path("all/", views.AggregatedResultsListView.as_view(), name="all"),
    path("recent uploads/", views.recent_results_bulk, name="recent_uploads"),
    path("list/", views.ResultListView.as_view(), name="list"),
    path("delete/<int:pk>/", views.ResultDeleteView.as_view(), name="delete"),
    path(
        "upload/",
        views.ResultUploadFormView.as_view(),
        name="upload_result_file",
    ),
    path("preview-upload/", views.preview_result_file, name="preview_upload"),
    path(
        "upload_format/<int:upload_type>",
        views.result_upload_file_format,
        name="upload_format"
    ),
    path(
        "delete by session/",
        views.CourseResultDeleteFormView.as_view(),
        name="delete_by_session",
    ),
    path(
        "download by session/", views.download_by_session, name="download_by_session"
    ),
    path(
        "transcript download/<str:reg_no>/",
        views.transcript_download_info,
        name="transcript_download_info",
    ),
    path(
        "transcript/<str:reg_no>/",
        views.StudentTranscriptGeneratorView.as_view(),
        name="generate_transcript",
    ),
    path(
        "spreadsheet/<str:expected_yr_of_grad>/",
        views.class_speadsheet_generator,
        name="generate_class_spreadsheet",
    ),
    path(
        "outstanding courses/class/<str:expected_yr_of_grad>/",
        views.class_outstanding_courses,
        name="class_outstanding_courses",
    ),
    path(
        "class of degree/class/<str:expected_yr_of_grad>/",
        views.possible_grads_with_class_of_degree,
        name="possible_class_of_degree"
    ),
    path(
        "collation/",
        views.ResultCollationByLevelOfStudyAnsSessionFormView.as_view(),
        name="collation",
    ),
    path(
        "result_collation/session=<str:session>/level=<str:level>/",
        views.result_collation,
        name="result_collation",
    ),
    path(
        "possible-graduands/<str:expected_yr_of_grad>",
        views.possible_graduands,
        name="possible_graduands",
    ),
    path("api/results/", views.results_list, name="api_results_list"),
    path("api/results/<int:pk>/", views.delete_result, name="api_delete_result"),
    path("api/results/bulk-delete/", views.bulk_delete_results, name="api_bulk_delete_results"),
    path("api/results/delete/entire-session/", views.delete_entire_semester_result, name="delete_entire_session"),
    path("api/results/aggregated/", views.aggregated_results_json, name="api_aggregated_results"),
    path("api/results/update/<int:pk>/", views.update_result, name="api_update_result"),
    path("api/results/create/", views.create_result, name="api_create_result"),
]
