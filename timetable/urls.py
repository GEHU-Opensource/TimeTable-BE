from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf import settings
from mainapp.logics.login import index
from django.urls import path, include, re_path
from django.views.static import serve
urlpatterns = [
    re_path(
            r'^TimeTable-FE/(?P<path>.*)$',
            serve,
            {
                'document_root': settings.BASE_DIR / 'static' / 'TimeTable-FE',
            },
        ),
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("", include("mainapp.urls")),
    path("mongo/", include('mainapp.urls'))
]
