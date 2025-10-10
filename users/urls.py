from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterViewSet, LoginViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'auth/register', RegisterViewSet, basename='auth-register')
router.register(r'auth/login', LoginViewSet, basename='auth-login')

urlpatterns = [
    path('', include(router.urls)),
]

