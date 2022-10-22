from django.urls.conf import path
from django.urls.resolvers import URLPattern
from .views import bios_main, edit_staff_bio, create_staff_bio, menu

app_name = "staff"

urlpatterns = [
    path("menu/", menu, name="menu"),
    path("bios/", bios_main, name="bios_main"),
    path("create/", create_staff_bio, name="create"),
    path("edit/<int:pk>", edit_staff_bio, name="edit"),
]
