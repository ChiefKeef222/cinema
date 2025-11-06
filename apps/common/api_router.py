from rest_framework.routers import DefaultRouter
from apps.movies.views import MovieViewSet
from apps.schedule.views import HallViewSet, SessionViewSet
from apps.booking.views import BookingViewSet

router = DefaultRouter()

router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"halls", HallViewSet, basename="hall")
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
