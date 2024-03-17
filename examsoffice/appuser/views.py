from typing import Any, Dict
from datetime import date
import subprocess
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from results.models import Lecturer, Student
from students.forms import StudentBioForm
from staff.forms import StaffBioForm
from .forms import AppUserForm
from examsoffice.settings import DATABASES

@method_decorator(login_required, name="dispatch")
class ProfileView(generic.TemplateView):
    """Profile view for user."""

    template_name = "appuser/profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        app_user = None
        if hasattr(self.request.user, "student"):
            app_user = self.request.user.student
        elif hasattr(self.request.user, "lecturer"):
            app_user = self.request.user.lecturer

        context = super().get_context_data(**kwargs)
        context["app_user"] = app_user

        return context


class ProfileUpdateFormView(generic.UpdateView):
    """Profile update view for user."""

    template_name = "appuser/profile_update.html"

    def get_success_url(self) -> str:
        return reverse("appuser:profile")

    def get_form_class(self):
        if hasattr(self.request.user, "student"):
            return StudentBioForm
        elif hasattr(self.request.user, "lecturer"):
            return StaffBioForm
        else:
            return AppUserForm

    def get_queryset(self):
        if hasattr(self.request.user, "student"):
            return Student.objects.all()
        elif hasattr(self.request.user, "lecturer"):
            return Lecturer.objects.all()
        else:
            return User.objects.all()


def generate_db_backup_file(request):
    """View generates db backup file."""
    template = "appuser/db_backup.html"
    backup_file_path = (
        Path(__file__).parent.parent.parent
        / "db_backup"
        / (
            f"studentdb_backup_{str(date.today().day).zfill(2)}"
            f"{str(date.today().month).zfill(2)}"
            f"{date.today().year}"
        )
    ).__str__()
    display_txt = ""
    try:
        subprocess.run(
            [
                '"C:\Program Files\PostgreSQL\13\bin\pg_dump"',
                f'-U {DATABASES["default"]["USER"]}',
                f'-p {DATABASES["default"]["PASSWORD"]}',
                f'{DATABASES["default"]["NAME"]}',
                f'-f "{backup_file_path}"'
            ],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as exc:
        display_txt = f"DB backup failed. Please contact administrator. {exc}"
    else:
        display_txt = (
            f"Backup successful. Backup file saved at {backup_file_path}")
    return render(request, template, {"message": display_txt})