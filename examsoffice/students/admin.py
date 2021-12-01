from django.contrib import admin

from results.models import Student

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    exclude = []

admin.site.register(Student, StudentAdmin)