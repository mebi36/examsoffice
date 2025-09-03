from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import add, view, course_list, api_update_course, api_bulk_update

app_name = "courses"

urlpatterns = [
    path("list/", view, name="list"),
    path("add/", add, name="add"),
    path("api/courses/", course_list, name="course_list"),
    path("api/courses/bulk-update/", api_bulk_update, name="api_bulk_update"),
    path("api/courses/update/<int:pk>/", api_update_course, name="api_update_course"),
]
