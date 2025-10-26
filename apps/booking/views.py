from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Booking
from .serializer import BookingCreateSerializer
from apps.schedule.models import Session, Seat


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request):
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)

        bookings = Booking.objects.filter(user=request.user).prefetch_related(
            "seats", "session"
        )
        data = []
        for b in bookings:
            seats_list = [
                {"row_number": s.row_number, "seat_number": s.seat_number}
                for s in b.seats.all()
            ]
            data.append(
                {
                    "id": b.id,
                    "session": str(b.session.public_id),
                    "seats": seats_list,
                    "created_at": b.created_at,
                }
            )
        return Response(data)

    @transaction.atomic
    def create(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_uuid = serializer.validated_data["session"]
        seat_coords = serializer.validated_data["seats"]

        try:
            session = Session.objects.get(public_id=session_uuid)
        except Session.DoesNotExist:
            return Response(
                {"error": "Сеанс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        hall_seats = []
        for coord in seat_coords:
            try:
                seat = Seat.objects.get(
                    hall=session.hall_id,
                    row_number=coord["row_number"],
                    seat_number=coord["seat_number"],
                )
                hall_seats.append(seat)
            except Seat.DoesNotExist:
                return Response(
                    {
                        "error": f"Место ряд={coord['row_number']}, номер={coord['seat_number']} не существует"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        already_booked = Booking.objects.filter(session=session, seats__in=hall_seats)
        if already_booked.exists():
            taken = []
            for b in already_booked:
                for s in b.seats.all():
                    taken.append(
                        {"row_number": s.row_number, "seat_number": s.seat_number}
                    )
            return Response(
                {"error": "Некоторые места уже заняты", "taken": taken},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = Booking.objects.create(session=session, user=request.user)
        booking.seats.add(*hall_seats)

        channel_layer = get_channel_layer()
        taken_seats = [{"row": s.row_number, "seat": s.seat_number} for s in hall_seats]
        async_to_sync(channel_layer.group_send)(
            f"session_{session.public_id}",
            {
                "type": "seat_update",
                "session_id": str(session.public_id),
                "taken_seats": taken_seats,
            },
        )

        return Response(
            {"message": "Бронирование успешно создано", "booking_id": booking.id},
            status=status.HTTP_201_CREATED,
        )


class SessionSeatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(public_id=session_id)
        except Session.DoesNotExist:
            return Response(
                {"error": "Сеансне найден"}, status=status.HTTP_404_NOT_FOUND
            )

        booked_seats = Seat.objects.filter(booked_seats__session=session).distinct()

        taken_seats = [
            {"row": seat.row_number, "seat": seat.seat_number} for seat in booked_seats
        ]

        return Response(
            {"sessionId": str(session.public_id), "takenSeats": taken_seats}
        )
