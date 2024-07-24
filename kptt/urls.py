from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", RedirectView.as_view(url=""), name="index"),
    path("learn/", include("learn.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
