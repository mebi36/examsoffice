from django.urls.conf import path

from .views import (
    GraduationClassInformationView,
    GraduationClassSearchFormView,
    graduation_class_info_json_view,
    graduation_class_student_json_view,
)

app_name = "graduationclasses"

urlpatterns = [
    path(
        "student/<str:student_reg_no>/",
        graduation_class_student_json_view,
        name="student_grad_class",
    ),
    path(
        "info/<str:year>/",
        GraduationClassInformationView.as_view(),
        name="info",
    ),
    path(
        "info/<str:grad_year>/json/",
        graduation_class_info_json_view,
        name="info-json",
    ),
    path("search/", GraduationClassSearchFormView.as_view(), name="search"),
]
