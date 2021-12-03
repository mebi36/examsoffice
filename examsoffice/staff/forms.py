from django.forms import ModelForm
from results.models import Lecturer

class StaffBioForm(ModelForm):
    
    
    class Meta:
        model = Lecturer
        fields = ['staff_number', 'title','first_name','last_name','other_names',
                    'email', 'head_of_dept']