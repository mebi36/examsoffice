from django.shortcuts import render
from django.contrib import messages

from results.models import Session, Semester, SemesterSession
from .forms import SessionForm
# Create your views here.

def view(request):
    template = "sessions/view.html"
    session_qs = Session.objects.all().order_by("-session")
    return render(request, template, {"sessions": session_qs})


def add(request):
    template = "sessions/add.html"
    context = {}

    if request.method == "GET":
        form = SessionForm()
        context = {"form": form}
        return render(request, template, context)
    elif request.method == "POST":
        form = SessionForm(request.POST)

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
        session_obj = (
            Session
            .objects
            .filter(session=form.cleaned_data["session"])
            .first()
        )
        semester_objs = Semester.objects.all()
        for semester in semester_objs:
            SemesterSession.objects.create(
                session=session_obj,
                semester=semester,
                desc=f"{session_obj.session} {semester.semester} Semester"
            )
        messages.add_message(
            request,
            messages.SUCCESS,
            "Save successful",
            extra_tags="text-success",
        )
        return render(request, template, {"form": form})