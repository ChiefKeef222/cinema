from django.utils import timezone
from django.db import transaction
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import Throttled
from drf_yasg.utils import swagger_auto_schema

from apps.booking.models import Booking, Payment, BookingStatus, PaymentStatus
from apps.schedule.models import Session, Seat
from .serializer import (
    BookingCreateSerializer,
    BookingListSerializer,
    PaymentSerializer,
)


class BookingPostThrottle(UserRateThrottle):
    scope = "booking"


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Booking.objects.select_related("session", "user").prefetch_related(
        "seats"
    )
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # throttle на весь ViewSet не ставим
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingListSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: BookingListSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        throttle = BookingPostThrottle()
        if not throttle.allow_request(request, self):
            raise Throttled(detail="Слишком много запросов, попробуйте через минуту")

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        booking.expires_at = timezone.now() + timezone.timedelta(minutes=15)

        # Schedule a task to check for booking expiration
        from .tasks import check_booking_expiration

        task = check_booking_expiration.apply_async(
            (booking.id,), eta=booking.expires_at
        )
        booking.task_id = task.id
        booking.save()

        channel_layer = get_channel_layer()
        taken_seats = list(
            Booking.objects.filter(
                session_id=booking.session.id,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            )
            .values_list("seats__id", flat=True)
            .distinct()
        )
        async_to_sync(channel_layer.group_send)(
            f"seat_updates_{booking.session.id}",
            {
                "type": "seat_update",
                "taken_seats": taken_seats,
            },
        )

        output = BookingListSerializer(booking)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_booking(self, request, public_id=None):
        booking = self.get_object()
        if booking.status in [BookingStatus.CONFIRMED, BookingStatus.PENDING]:
            if booking.task_id:
                from config.celery import app as celery_app

                celery_app.control.revoke(booking.task_id)

            booking.status = BookingStatus.CANCELLED
            booking.save(update_fields=["status"])
            return Response({"detail": "Бронь успешно отменена."})
        return Response(
            {"detail": "Бронь нельзя отменить."}, status=status.HTTP_400_BAD_REQUEST
        )


class PaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(public_id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Бронь не найдена."}, status=status.HTTP_404_NOT_FOUND
            )

        if booking.status == BookingStatus.CANCELLED:
            return Response(
                {"error": "Эта бронь уже отменена."}, status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == BookingStatus.CONFIRMED:
            return Response(
                {"error": "Эта бронь уже оплачена."}, status=status.HTTP_400_BAD_REQUEST
            )

        if booking.expires_at and timezone.now() > booking.expires_at:
            booking.status = BookingStatus.EXPIRED  # Changed from CANCELLED
            booking.save(update_fields=["status"])
            return Response(
                {"error": "Время брони истекло."}, status=status.HTTP_400_BAD_REQUEST
            )

        if booking.task_id:
            from config.celery import app as celery_app

            celery_app.control.revoke(booking.task_id)

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            status=PaymentStatus.PAID,
            paid_at=timezone.now(),
        )

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status"])

        channel_layer = get_channel_layer()
        taken_seats = [
            {"row_number": s.row_number, "seat_number": s.seat_number}
            for s in booking.seats.all()
        ]
        async_to_sync(channel_layer.group_send)(
            f"session_{booking.session.public_id}",
            {
                "type": "seat_update",
                "session_id": str(booking.session.public_id),
                "taken_seats": taken_seats,
            },
        )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SessionSeatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(public_id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Сеанс не найден"}, status=404)

        booked_seats = Seat.objects.filter(
            bookings__session=session,
            bookings__status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        ).distinct()

        taken_seats = [
            {"row_number": seat.row_number, "seat_number": seat.seat_number}
            for seat in booked_seats
        ]

        return Response(
            {"sessionId": str(session.public_id), "takenSeats": taken_seats}
        )
