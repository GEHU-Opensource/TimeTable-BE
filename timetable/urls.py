from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from mainapp.logics.login import index

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("", include("mainapp.urls")),
    path("mongo/", include('mainapp.urls'))
]
