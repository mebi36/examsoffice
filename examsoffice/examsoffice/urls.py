"""examsoffice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.urls.conf import include
from django.views.generic import TemplateView

from index import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("results/", include("results.urls")),
    path("students/", include("students.urls")),
    path("staff/", include("staff.urls")),
    path("programs/", include("programs.urls")),
    path("courses/", include("courses.urls")),
    path("graduation-classes/", include("graduationclasses.urls")),
    path("", views.index_view, name="index"),
    path("index/", include("index.urls")),
    path("users/", include("appuser.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urlpatterns = urlpatterns + [
#     re_path("^.", TemplateView.as_view(template_name='404.html')),
# ]
