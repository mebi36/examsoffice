from django.urls.conf import path
from django.urls.resolvers import URLPattern

from .views import add, view

app_name = "sessions"

urlpatterns = [
    path("view/", view, name="view"),
    path("add/", add, name="add"),
]