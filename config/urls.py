from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("admin/", admin.site.urls),
    path("api/movies/", include("apps.movies.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/schedule/", include("apps.schedule.urls")),
    path("api/booking/", include("apps.booking.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
