from django.forms.models import ModelForm

from results.models import Session
from examsoffice.utils.forms import add_bootstrap_formatting


class SessionForm(ModelForm):
    required_css_class = "required"
    error_css_class = "error"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)
    
    class Meta:
        model = Session
        exclude = []
    
    def clean(self):
        super().clean()

        existing_sessions_qs = Session.objects.filter(
            session=self.cleaned_data["session"]
        ).count()
        if existing_sessions_qs > 0:
            self.add_error(
                None, "Session already exists! This is a form error"
            )
