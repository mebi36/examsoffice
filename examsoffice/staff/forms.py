from django.forms import ModelForm
from results.models import Lecturer
from django.core.exceptions import ValidationError


class StaffBioForm(ModelForm):
    
    
    class Meta:
        model = Lecturer
        fields = ['staff_number', 'title','first_name','last_name','other_names',
                    'email', 'head_of_dept']

    def clean_staff_number(self):
        staff_num = self.cleaned_data['staff_number'].upper()
        if not Lecturer.is_valid_staff_no(staff_num):
            self.add_error("staff_number",
                '''Invalid Staff ID. Ensure your entry begins 
                    with 'SS.' followed by the actual number''')
        
        return staff_num

    def clean_head_of_dept(self):
        head_of_dept = self.cleaned_data['head_of_dept']
        if head_of_dept == True:
            try:
                outgoing_hod = Lecturer.objects.get(head_of_dept=True)
            except:
                pass
            else:
                outgoing_hod.head_of_dept = False
                outgoing_hod.save(update_fields=['head_of_dept'])
        
        return head_of_dept


class CreateStaffBioForm(StaffBioForm):

    def clean_staff_number(self):
        super().clean_staff_number()
        staff_num = self.cleaned_data['staff_number'].upper()
        staff_qs = Lecturer.objects.filter(staff_number__iexact=staff_num)

        if len(staff_qs) > 0:
            self.add_error("staff_number", "Staff already exists")

        return staff_num
