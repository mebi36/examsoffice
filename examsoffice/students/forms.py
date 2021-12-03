from django import forms
from django.forms.models import inlineformset_factory

from results.models import Student, StudentProgressHistory

def add_bootstrap_formatting(self):
    for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control w-75'


class StudentBioForm(forms.ModelForm):
    student_reg_no = forms.CharField(max_length=12,required=True,disabled=True)
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)    
            add_bootstrap_formatting(self)


    class Meta:
        model = Student 
        # exclude = ['student_photo']
        fields = ['student_reg_no', 'last_name', 'first_name', 'other_names', 'email',
                'phone_number', 'sex', 'marital_status', 'date_of_birth', 
                'town_of_origin', 'lga_of_origin', 'state_of_origin', 'nationality',
                'mode_of_admission', 'level_admitted_to', 'mode_of_study',
                'year_of_admission', 'expected_yr_of_grad', 'graduated', 'address_line1',
                'address_line2', 'city', 'state', 'country', 'class_rep', 'current_level_of_study', 'cgpa']


ProgressHistoryFormSet = inlineformset_factory(
                                Student,
                                StudentProgressHistory,
                                min_num=1,
                                extra=1,
                                exclude=[])    


class ProgressHistoryForm(forms.ModelForm):


        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)    
            add_bootstrap_formatting(self)
            self.fields['student_reg_no'].widget = forms.HiddenInput()

        class Meta:
                model = StudentProgressHistory
                exclude = []