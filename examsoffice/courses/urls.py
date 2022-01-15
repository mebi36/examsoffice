from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import (add, view)
app_name = 'courses'

urlpatterns = [
    path('view/', view, name='view'),
    path('add/', add, name='add'),

]