from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (
    edit_bio_data,
    students_menu,
)
app_name = 'students'

urlpatterns = [
    path('',students_menu, name='menu'),
    path('bio/<str:reg_no>',edit_bio_data,name='edit_bio'),
]