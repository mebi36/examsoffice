from django.db.models.functions import Upper
from results.models import Result


def transform_grades_to_uppercase():
    # Update all Result entries to have uppercase grades
    Result.objects.all().update(letter_grade=Upper('letter_grade'))
