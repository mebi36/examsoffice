from django.urls.conf import path
from .views import (
    create_bio_data,
    edit_bio_data,
    students_menu,
    update_progress_history,
    bio_update_format,
    upload_bio_file,
    profile,
    StudentProfileSearchView,
    StudentProfileSearchResultListView,
)

app_name = "students"

urlpatterns = [
    path("", students_menu, name="menu"),
    path("profile/<str:reg_no>/", profile, name="profile"),
    path("bio/<str:reg_no>", edit_bio_data, name="edit_bio"),
    # path('bio2/<int:pk>', StudentUpdateView.as_view(), name='edit_bio'),
    path("create bio/<str:reg_no>/", create_bio_data, name="create_bio"),
    path("search/", StudentProfileSearchView.as_view(), name="search"),
    path(
        "search-results/<path:search>/",
        StudentProfileSearchResultListView.as_view(),
        name="search-results",
    ),
    path(
        "progress history/<str:reg_no>",
        update_progress_history,
        name="progress_history",
    ),
    path("bio update format/", bio_update_format, name="bio_update_format"),
    path("bio update format/upload", upload_bio_file, name="upload_bio_file"),
]
