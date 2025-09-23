import json

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from results.models import Course
from .forms import CourseForm


def view(request):
    template = "courses/view.html"
    courses_qs = Course.objects.all().order_by("-id")

    return render(request, template, {"courses": courses_qs})


def add(request):
    template = "courses/add.html"
    context = {}

    if request.method == "GET":
        form = CourseForm()
        context = {"form": form}
        return render(request, template, context)

    elif request.method == "POST":
        form = CourseForm(request.POST)

        if not form.is_valid():
            messages.add_message(
                request,
                messages.ERROR,
                "Form entry invalid.",
                extra_tags="text-danger",
            )
            context = {"form": form}
            return render(request, template, context)

        form.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            "Save successful",
            extra_tags="text-success",
        )
        return render(request, template, {"form": form})


def course_list(request):
    qs = Course.objects.all().order_by("course_code")
    return JsonResponse(list(qs.values()), safe=False)


@require_http_methods(["POST"])
def api_update_course(request, pk):
    
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found."}, status=404)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    print(f"{body= }")
    for key, value in body.items():
        try:
            setattr(course, key, value)
        except Exception as e:
            print(e)
            continue
    course.save()
    return JsonResponse({"message": "Course updated successfully."})


@require_http_methods(["POST"])
def api_bulk_update(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    updated_courses = []
    for item in data.get("courses", []):
        try:
            course = Course.objects.get(id=item["id"])
            course.archived = item["archived"]
            course.save()
            updated_courses.append({
                "id": course.id,
                "archived": course.archived
            })
        except Course.DoesNotExist:
            continue
    return JsonResponse(updated_courses, safe=False)
