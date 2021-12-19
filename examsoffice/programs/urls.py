from django.urls.conf import path
from .views import ( menu, add_prog_requirement_form,
                    edit_prog_req)
app_name = 'programs'
urlpatterns = [
    path('', menu, name='menu'),
    path('program requirement/add/form', add_prog_requirement_form, name='add_prog_requirement_form'),
    path('program requirement/edit/<str:session>/<str:level_of_study>/', edit_prog_req, name='edit_prog_req'),
]