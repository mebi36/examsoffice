from django.forms.models import ModelForm
from results.models import Course, LevelOfStudy
from students.forms import add_bootstrap_formatting

# CourseForm = modelform_factory(Course, exclude=[])


class CourseForm(ModelForm):
    required_css_class = "required"
    error_css_class = "error"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)
        self.fields["course_level"].queryset = LevelOfStudy.objects.filter(
            level__lte=5
        )

    class Meta:
        model = Course
        exclude = []

    def clean(self):
        super().clean()

        existing_courses_qs = Course.objects.filter(
            course_title__iexact=self.cleaned_data["course_title"],
            course_code__iexact=self.cleaned_data["course_code"],
            credit_load=self.cleaned_data["credit_load"],
        ).count()
        if existing_courses_qs > 0:
            self.add_error(
                None, "Course already exists!!! This is a form error"
            )
