from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory

from examsoffice.utils.forms import add_bootstrap_formatting
from results.models import Student, StudentProgressHistory


class StudentProfileSearchForm(forms.Form):
    """Form for finding a student obj by registration number."""
    student_reg_no = forms.CharField(label="Registration Number", max_length=12, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)
    
    def clean_student_reg_no(self):
        student_reg_no = self.cleaned_data['student_reg_no']

        if not Student.is_valid_reg_no(student_reg_no):
            raise ValidationError("Invalid student registration number")

        if not Student.objects.filter(student_reg_no=student_reg_no).exists():
            raise ValidationError("No registered student found with the provided registration number")

        return student_reg_no

class StudentBioForm(forms.ModelForm):
    student_reg_no = forms.CharField(
        max_length=12, required=True, disabled=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)

    class Meta:
        model = Student
        # exclude = ['student_photo']
        fields = [
            "student_reg_no",
            "last_name",
            "first_name",
            "other_names",
            "expected_yr_of_grad",
            "email",
            "phone_number",
            "sex",
            "marital_status",
            "date_of_birth",
            "town_of_origin",
            "lga_of_origin",
            "state_of_origin",
            "nationality",
            "mode_of_admission",
            "level_admitted_to",
            "mode_of_study",
            "year_of_admission",
            "graduated",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "country",
            "class_rep",
            "current_level_of_study",
        ]


ProgressHistoryFormSet = modelformset_factory(
    StudentProgressHistory,
    extra=1,
    can_delete=True,
    exclude=[],
    widgets={"student_reg_no": forms.HiddenInput},
)

# class ProgressHistoryForm(forms.ModelForm):


#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             add_bootstrap_formatting(self)
#             self.fields['student_reg_no'].widget = forms.HiddenInput()

#         class Meta:
#                 model = StudentProgressHistory
#                 exclude = []
