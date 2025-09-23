from django.urls.conf import path
from django.urls.resolvers import URLPattern

from .views import add, view, api_semester_session_list

app_name = "sessions"

urlpatterns = [
    path("view/", view, name="view"),
    path("add/", add, name="add"),
    path("api/sessions/", api_semester_session_list, name="api_list")
]