from django import forms
from django.forms.models import inlineformset_factory
from django.forms import fields

from results.models import Student, StudentProgressHistory

def add_bootstrap_formatting(self):
    for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control w-75'


class StudentBioForm(forms.ModelForm):
    student_reg_no = forms.CharField(max_length=12,required=True)
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)    
            add_bootstrap_formatting(self)


    class Meta:
        model = Student 
        exclude = []


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