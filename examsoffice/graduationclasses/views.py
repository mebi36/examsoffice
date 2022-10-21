from typing import Any, Dict
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views import generic
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
        return HttpResponseBadRequest("Student's Expected Year of Graduation unknown")

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
    # context["top_student"] = [student.values("student_reg_no", "first_name", "last_name") for student in grad_class.best_student()]
    context["top_student"] = [{"reg_no": student.student_reg_no, "first_name": student.first_name, "last_name": student.last_name, "cgpa": student.cgpa, "url": student.get_absolute_url()} for student in grad_class.best_student()]


    return JsonResponse(context, safe=False)


class GraduationClassInformationView(generic.TemplateView):
    """View for displaying a graduation class. 
    
    View contains info such as: members, class performance statistics, links
    to download class-wide spreadsheets, etc.
    """
    template_name: str = "graduationclasses/info.html"
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context["graduation_class"] = GraduationClass(self.kwargs["year"])
        return context

