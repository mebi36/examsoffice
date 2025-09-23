from typing import Any
from django.db import models

from django.core.exceptions import ValidationError
from results.models import Result, Course, SemesterSession


# Create your models here.
class AnalyticsData(models.Model):
    """Model to temporarily hold analytics data"""
    name = models.CharField(max_length=255, unique=True)
    results = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
