"""URL patterns for the results app."""

from django.urls.conf import path

from results import views

app_name = "results"

urlpatterns = [
    path("edit/<int:pk>/", views.ResultObjectUpdateView.as_view(), name="edit"),
    path("detail/<int:pk>/", views.ResultObjectDetailView.as_view(), name="detail"),
    path("student/<str:reg_no>/", views.StudentAcademicRecordsListView.as_view(), name="student-records"),
    path("add/<str:reg_no>/", views.ResultCreateView.as_view(), name="add"),

    path("all/", views.AggregatedResultsListView.as_view(), name="all"),
    path("recent uploads/", views.recent_results_bulk, name="recent_uploads"),
    path("list/", views.ResultListView.as_view(), name="list"),
    path("delete/<int:pk>/", views.ResultDeleteView.as_view(), name="delete"),
    path("upload/", views.ResultFileFormatFormView.as_view(), name="upload"),
    path("upload file/", views.ResultUploadFormView.as_view(), name="upload_result_file"),
    path("delete by session/", views.CourseResultDeleteFormView.as_view(), name="delete_by_session"),
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
    path("collation/", views.ResultCollationByLevelOfStudyAnsSessionFormView.as_view(), name="collation"),
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
]
