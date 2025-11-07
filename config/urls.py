from django.contrib import admin
from django.urls import path, include, re_path
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Сinema API",
        default_version="v1",
        description="Документация REST API для кинотеатра",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="aarhat144@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("admin/", admin.site.urls),
    path("api/", include("apps.common.api_router")),
    path(
        "api/sessions/<uuid:session_id>/seats/",
        include("apps.booking.urls_extra"),
    ),
    # Swagger UI
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
