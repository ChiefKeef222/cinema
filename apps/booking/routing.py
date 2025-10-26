from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path("ws/session/<uuid:session_id>/seats/", consumer.SeatConsumer.as_asgi()),
]
