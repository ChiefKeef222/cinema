from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BookingViewSet, SessionSeatsView

router = DefaultRouter()
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path('', include(router.urls)),
    path('sessions/<uuid:session_id>/seats/', SessionSeatsView.as_view(), name='session-seats'),
]
