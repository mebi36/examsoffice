from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (
    create_bio_data,
    edit_bio_data,
    students_menu,
    search,
    update_progress_history,
    # StudentUpdateView,
)
app_name = 'students'

urlpatterns = [
    path('',students_menu, name='menu'),
    path('bio/<str:reg_no>', edit_bio_data, name='edit_bio'),
    # path('bio2/<int:pk>', StudentUpdateView.as_view(), name='edit_bio'),
    path('create bio/<str:reg_no>/', create_bio_data, name='create_bio'),
    path('search/', search, name='search'),
    path('progress history/<str:reg_no>', update_progress_history, 
                                        name='progress_history'),
]