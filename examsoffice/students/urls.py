from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (
    edit_bio_data,
    students_menu,
    search,
    update_progress_history,
)
app_name = 'students'

urlpatterns = [
    path('',students_menu, name='menu'),
    # path('bio/', edit_bio_data, name='edit_bio_blank'),
    path('bio/reg_no=<str:reg_no>', edit_bio_data, name='edit_bio'),
    path('search/', search, name='search'),
    path('progress history/<str:reg_no>', update_progress_history, 
                                        name='progress_history'),
]