from rest_framework import serializers

from courses.serializers import CourseSerializer
from results.models import Result


class ResultSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)

    class Meta:
        model = Result
        fields = "__all__"
