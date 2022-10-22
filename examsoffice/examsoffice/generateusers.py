from django.contrib.auth.models import User
from results.models import Lecturer


def generate_users():
    unregistered_staff = Lecturer.objects.filter(user__isnull=True)

    for staff in unregistered_staff:
        user_obj = User.objects.create_user(username=staff.staff_number)
        staff.user = user_obj
        staff.save()


def register_user(staff_number, password=None, **kwargs):
    staff = Lecturer.objects.filter(staff_number=staff_number)

    if staff:
        staff = staff.first()
        user_obj = User.objects.create_user(username=staff.staff_number, is_staff=True, **kwargs)
        user_obj.set_password(password or staff_number.lower())
        user_obj.save()
        staff.user = user_obj
        staff.save()
        print("%s registered" % staff.full_name)
    else:
        print("No staff found with provided staff number (%s)"%staff_number)