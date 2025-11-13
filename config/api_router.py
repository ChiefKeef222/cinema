from rest_framework.routers import DefaultRouter
from apps.movies.views import MovieViewSet
from apps.schedule.views import HallViewSet, SessionViewSet
from apps.users.views import RegisterViewSet, LoginViewSet, RefreshViewSet
from apps.booking.views import BookingViewSet

router = DefaultRouter()

router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"halls", HallViewSet, basename="hall")
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"auth/register", RegisterViewSet, basename="auth-register")
router.register(r"auth/login", LoginViewSet, basename="auth-login")
router.register(r"auth/refresh", RefreshViewSet, basename="auth-refresh")

urlpatterns = router.urls
