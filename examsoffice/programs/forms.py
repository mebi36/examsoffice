from django.forms import modelformset_factory
from results.models import ProgramRequirement

prog_req_formset = modelformset_factory(ProgramRequirement, fields=(
                    'mode_of_admission', 'course'), extra=2, can_delete=True
                )