# apps/booking/urls_extra.py
from django.urls import path
from .views import SessionSeatsView

urlpatterns = [
    path("", SessionSeatsView.as_view(), name="session-seats"),
]