from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import graduation_class_student_view

app_name="graduationclasses"

urlpatterns = [
    path("student/<str:student_reg_no>/", graduation_class_student_view, name="student_grad_class")
]