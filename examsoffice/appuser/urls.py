from django.urls.conf import path

from appuser.views import ProfileUpdateFormView, ProfileView

app_name = "appuser"
urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/<int:pk>/", ProfileUpdateFormView.as_view(), name="edit-profile"),
]