from django.urls.conf import path
from django.urls.resolvers import URLPattern

from index.views import download_info, general_messages


app_name = "index"

urlpatterns = [
    path("downloads/", download_info, name="download_info"),
    path("info/", general_messages, name="general_messages"),
]
