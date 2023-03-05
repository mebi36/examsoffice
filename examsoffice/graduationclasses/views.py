from typing import Any, Dict

from django.forms import Form
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponse,
)
from django.http.response import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse

from graduationclasses.forms import GraduationClassInfoSearchForm

from .graduationclass import GraduationClass
from results.models import Student


def graduation_class_student_json_view(request, student_reg_no: str):
    """
    This view returns relevant data about the class a student
    belongs to.
    """
    student_reg_no = student_reg_no.replace("_", "/")

    if not Student.is_valid_reg_no(student_reg_no):
        return HttpResponseBadRequest("Invalid Student Registration Number")

    student = Student.objects.filter(student_reg_no=student_reg_no)

    if not student.exists():
        return HttpResponseNotFound("Student Registration Number not found")

    student = student.first()

    if student.expected_yr_of_grad is None:
        return HttpResponseBadRequest(
            "Student's Expected Year of Graduation unknown"
        )

    grad_class = GraduationClass(student.expected_yr_of_grad)

    context = {}
    context["position_in_class"] = grad_class.student_position(student_reg_no)
    context["class_average_cgpa"] = grad_class.average_cgpa()
    context["class_size"] = len(grad_class.members)

    return JsonResponse(context, safe=False)


def graduation_class_info_json_view(request, grad_year: str):
    """Retrieve grad class data that takes long to process."""
    grad_class = GraduationClass(grad_year)
    context = {}
    context["class_average_cgpa"] = grad_class.average_cgpa()
    context["top_student"] = [
        {
            "reg_no": student.student_reg_no,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "cgpa": student.current_cgpa,
            "url": student.get_absolute_url(),
        }
        for student in grad_class.best_student()
    ]
    return JsonResponse(context, safe=False)


def graduation_class_cgpa_breakdown_json_view(request, grad_year: str):
    """Retrieve grad class cgpa breakdown."""
    grad_class = GraduationClass(grad_year)
    context = {}
    context["class_cgpa_breakdown"] = grad_class.cgpa_breakdown()
    return JsonResponse(context, safe=False)


@method_decorator(login_required, name="dispatch")
class GraduationClassInformationView(generic.TemplateView):
    """View for displaying a graduation class.

    View contains info such as: members, class performance statistics, links
    to download class-wide spreadsheets, etc.
    """

    template_name: str = "graduationclasses/info.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["graduation_class"] = GraduationClass(self.kwargs["year"])
        return context


@method_decorator(login_required, name="dispatch")
class GraduationClassSearchFormView(generic.FormView):
    """Generate spreadsheet of outstanding courses for selected grad set."""

    template_name: str = "graduationclasses/search.html"
    form_class: Form = GraduationClassInfoSearchForm

    def form_valid(self, form: Form) -> HttpResponse:
        url: str = reverse(
            "graduationclasses:info",
            kwargs={"year": form.cleaned_data["expected_yr_of_grad"]},
        )
        return HttpResponseRedirect(url)


# TODO add view to change level of study of entire graduationclass