from celery import shared_task
from django.utils import timezone
from .models import Booking, BookingStatus
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging


logger = logging.getLogger(__name__)


@shared_task
def check_booking_expiration(booking_id: int):
    """
    Checks if a booking has expired and updates its status.
    If the booking has expired, it also sends a WebSocket message to notify clients.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        logger.warning(f"Booking with id {booking_id} not found.")
        return

    if booking.status == BookingStatus.PENDING and booking.expires_at < timezone.now():
        booking.status = BookingStatus.EXPIRED
        booking.save()

        # Notify clients via WebSocket
        channel_layer = get_channel_layer()
        session_id = booking.session.id
        taken_seats = list(
            Booking.objects.filter(
                session_id=session_id,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            )
            .values_list("seats__id", flat=True)
            .distinct()
        )

        async_to_sync(channel_layer.group_send)(
            f"seat_updates_{session_id}",
            {
                "type": "seat_update",
                "taken_seats": taken_seats,
            },
        )
        logger.info(
            f"Booking {booking_id} expired and status updated. WebSocket message sent."
        )


@shared_task
def check_all_expired_bookings():
    """
    Periodically checks all pending bookings and marks them as expired if needed.
    """
    expired_bookings = Booking.objects.filter(
        status=BookingStatus.PENDING, expires_at__lt=timezone.now()
    )
    count = expired_bookings.count()
    if count > 0:
        for booking in expired_bookings:
            check_booking_expiration.delay(booking.id)
        logger.info(f"Found and triggered expiration check for {count} bookings.")
    else:
        logger.info("No expired bookings found.")
