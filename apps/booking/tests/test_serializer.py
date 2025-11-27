import pytest
from rest_framework.exceptions import ValidationError
from django.test import RequestFactory

from apps.booking.serializer import (
    BookingCreateSerializer,
    BookingListSerializer,
    PaymentSerializer,
)
from apps.booking.models import Booking, BookingStatus, PaymentStatus
from apps.schedule.models import Seat, Hall, Session
from apps.users.models import User


@pytest.fixture
def seats(db, hall: Hall) -> list[Seat]:
    return [
        Seat.objects.create(hall=hall, row_number=1, seat_number=1),
        Seat.objects.create(hall=hall, row_number=1, seat_number=2),
    ]


@pytest.fixture
def booking(db, user: User, session: Session, seats: list[Seat]) -> Booking:
    b = Booking.objects.create(user=user, session=session)
    b.seats.set(seats)
    b.save()
    return b


@pytest.mark.django_db
class TestBookingSerializers:
    def test_booking_create_serializer_valid(self, session, seats, user):
        factory = RequestFactory()
        request = factory.post("/fake-url/")
        request.user = user

        data = {
            "session": str(session.public_id),
            "seats": [
                {"row_number": seat.row_number, "seat_number": seat.seat_number}
                for seat in seats
            ],
        }
        serializer = BookingCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(raise_exception=True)

        booking_instance = serializer.save()
        assert booking_instance.user == user
        assert booking_instance.session == session
        assert booking_instance.seats.count() == len(seats)

    def test_booking_create_serializer_invalid_session(self, seats, user, hall):
        import uuid

        factory = RequestFactory()
        request = factory.post("/fake-url/")
        request.user = user

        data = {
            "session": str(uuid.uuid4()),
            "seats": [
                {"row_number": seat.row_number, "seat_number": seat.seat_number}
                for seat in seats
            ],
        }
        serializer = BookingCreateSerializer(data=data, context={"request": request})
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Сеанс не найден" in str(excinfo.value)

    def test_booking_create_serializer_seat_already_taken(self, session, seats, user):
        other_user = User.objects.create_user(
            username="otheruser", email="other@user.com", password="Barsik_04"
        )
        existing_booking = Booking.objects.create(
            user=other_user, session=session, status=BookingStatus.CONFIRMED
        )
        existing_booking.seats.add(seats[0])

        factory = RequestFactory()
        request = factory.post("/fake-url/")
        request.user = user

        data = {
            "session": str(session.public_id),
            "seats": [
                {"row_number": seats[0].row_number, "seat_number": seats[0].seat_number}
            ],
        }
        serializer = BookingCreateSerializer(data=data, context={"request": request})
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Некоторые места уже заняты" in str(excinfo.value)

    def test_booking_list_serializer(self, booking: Booking):
        serializer = BookingListSerializer(instance=booking)
        data = serializer.data
        assert data["id"] == str(booking.public_id)
        assert data["status"] == BookingStatus.PENDING
        assert data["session_title"] == booking.session.movie.title
        assert len(data["seats"]) == booking.seats.count()
        assert data["seats"][0]["row_number"] == booking.seats.first().row_number

    def test_payment_serializer_create(self, booking: Booking):
        data = {"booking": booking.pk}  # Payment serializer expects pk
        serializer = PaymentSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

        payment_instance = serializer.save()
        assert payment_instance.booking == booking
        assert payment_instance.amount == booking.total_amount
        assert payment_instance.status == PaymentStatus.PENDING
