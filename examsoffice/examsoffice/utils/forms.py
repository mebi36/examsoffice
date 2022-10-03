"""Generic form objects."""

def add_bootstrap_formatting(self):
    """Add bootstrap classes to form fields."""
    for form_field in self.fields:
        self.fields[form_field].widget.attrs["class"] = "form-control"