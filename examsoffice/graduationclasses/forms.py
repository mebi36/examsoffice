from datetime import date

from django import forms

from examsoffice.utils.forms import add_bootstrap_formatting


class GraduationClassInfoSearchForm(forms.Form):
    """Find a graduation class info."""

    gradudation_set_choices = sorted(
        [(year, year) for year in range(2017, (date.today().year + 5))],
        reverse=True,
    )
    expected_yr_of_grad = forms.ChoiceField(
        choices=gradudation_set_choices,
        label="Class Expected Year of Graduation",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_formatting(self)
