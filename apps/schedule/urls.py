from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HallViewSet, SessionViewSet

router = DefaultRouter()
router.register(r"halls", HallViewSet, basename="hall")
router.register(r"sessions", SessionViewSet, basename="session")

urlpatterns = [
    path("", include(router.urls)),
]
