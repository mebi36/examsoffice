from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound

from .graduationclass import GraduationClass
from results.models import Student


def graduation_class_student_view(request, student_reg_no: str):
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