from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/movies/", include("apps.movies.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/schedule", include("apps.schedule.urls")),
]
