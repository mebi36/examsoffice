from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (
    students_menu,
)
app_name = 'students'

urlpatterns = [
    path('',students_menu, name='students_menu'),
]