from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from results.models import Result, Course, SemesterSession, Session
from examsoffice.utils.forms import add_bootstrap_formatting


class ResultForm(forms.ModelForm):
    """Model form for Result model."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)

    class Meta:
        model = Result
        fields = ["student_reg_no", "course", "semester", "letter_grade"]


class ResultFileUploadFormatOptionForm(forms.Form):
    """Presents user with available result file formats the system accepts."""

    RESULT_UPLOAD_OPTIONS = [
        ("Upload results without scores", "Upload results without scores"),
        ("Upload results with scores", "Upload results with scores"),
    ]
    upload_option = forms.ChoiceField(choices=RESULT_UPLOAD_OPTIONS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)


class CourseResultForm(forms.Form):
    """A form for operations on results for an entire course/session."""

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), label="Select Course", required=True
    )
    semester = forms.ModelChoiceField(
        queryset=SemesterSession.objects.all(),
        label="Select Session/Semester",
        required=True,
    )

    def clean(self):
        if (
            self.cleaned_data["course"].course_semester
            != self.cleaned_data["semester"].semester
        ):
            raise ValidationError("Course/Semester mismatch")
        return super().clean()


class ResultFileUploadForm(CourseResultForm):
    """Form for users to upload result files."""

    result_file = forms.FileField(
        label="Select Result File (CSV)", allow_empty_file=False, required=True
    )
    skip_existing_rows = forms.BooleanField(
        label="Skip students that already have a result for selected course and semester",
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set necessary attributes on form fields
        for form_field in self.fields:
            if form_field == "skip_existing_rows":
                continue
            if form_field == "result_file":
                self.fields[form_field].widget.attrs["accept"] = ".csv"

            self.fields[form_field].widget.attrs["class"] = "form-control"


class CourseResultDeletionForm(CourseResultForm):
    """A form for deleting all results for a course for a session/semester."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)


class ResultCollationBySessionAndLevelOfStudyForm(forms.Form):
    """Select level of study and academic session for result collation sheet."""

    level_of_study = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 6)], label="Level of Study"
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all().order_by("-session"),
        label="Academic Session",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)