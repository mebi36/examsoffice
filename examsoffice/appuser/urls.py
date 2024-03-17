from django.urls.conf import path

from appuser.views import (
    ProfileUpdateFormView, ProfileView, generate_db_backup_file)

app_name = "appuser"
urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "profile/edit/<int:pk>/",
        ProfileUpdateFormView.as_view(),
        name="edit-profile",
    ),
    path("create-backup", generate_db_backup_file, name="db_backup"),
]
