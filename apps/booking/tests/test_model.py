import pytest
from datetime import timedelta
from rest_framework.exceptions import ValidationError

from apps.schedule.models import Hall, Session, Seat
from apps.booking.models import Booking, Payment, BookingStatus, PaymentStatus
from apps.users.models import User

# Import shared fixtures from the project's dedicated fixtures directory


# This fixture is specific to booking tests and can remain here.
@pytest.fixture
def seats(db, hall: Hall) -> list[Seat]:
    seat1 = Seat.objects.create(hall=hall, row_number=1, seat_number=1)
    seat2 = Seat.objects.create(hall=hall, row_number=1, seat_number=2)
    return [seat1, seat2]


# A booking fixture that relies on the imported fixtures
@pytest.fixture
def booking(db, user: User, session: Session, seats: list[Seat]) -> Booking:
    b = Booking.objects.create(user=user, session=session)
    b.seats.set(seats)
    b.save()  # Ensure total_amount is calculated
    return b


@pytest.mark.django_db
class TestBookingModels:
    def test_booking_creation(
        self, booking: Booking, user: User, session: Session, seats: list[Seat]
    ):
        """Test that a booking can be created and its fields are correct."""
        assert booking.user == user
        assert booking.session == session
        assert booking.status == BookingStatus.PENDING
        assert list(booking.seats.all()) == seats
        assert booking.pk is not None

    def test_booking_save_logic(self, booking: Booking, session: Session):
        """Test the custom save method of the Booking model."""
        assert booking.expires_at is not None
        expected_expiry = booking.created_at + timedelta(minutes=15)
        assert abs(booking.expires_at - expected_expiry) < timedelta(seconds=1)
        assert booking.total_amount == session.price * booking.seats.count()

    def test_booking_str_representation(self, booking: Booking, session, user):
        """Test the __str__ method of the Booking model."""
        seats_list = ", ".join(
            [f"ряд {s.row_number}, место {s.seat_number}" for s in booking.seats.all()]
        )
        expected_str = f"{user} | {session} | {seats_list}"
        assert str(booking) == expected_str

    def test_payment_creation(self, booking: Booking):
        """Test that a Payment can be created for a booking."""
        payment = Payment.objects.create(booking=booking, amount=booking.total_amount)
        assert payment.booking == booking
        assert payment.amount == booking.total_amount
        assert payment.status == PaymentStatus.PENDING
        assert payment.pk is not None
        assert str(payment) == f"Оплата #{payment.id} | {booking.user} | Ожидание"

    def test_payment_mark_as_paid(self, booking: Booking):
        """Test the mark_as_paid method on the Payment model."""
        payment = Payment.objects.create(booking=booking, amount=booking.total_amount)
        payment.mark_as_paid()

        payment.refresh_from_db()
        booking.refresh_from_db()

        assert payment.status == PaymentStatus.PAID
        assert payment.paid_at is not None
        assert booking.status == BookingStatus.CONFIRMED

    def test_payment_mark_as_failed(self, booking: Booking):
        """Test the mark_as_failed method on the Payment model."""
        payment = Payment.objects.create(booking=booking, amount=booking.total_amount)
        payment.mark_as_failed()

        payment.refresh_from_db()
        booking.refresh_from_db()

        assert payment.status == PaymentStatus.FAILED
        assert booking.status == BookingStatus.CANCELLED

    def test_payment_for_cancelled_booking_fails(self, booking: Booking):
        """Test that a payment cannot be created for a cancelled booking."""
        booking.status = BookingStatus.CANCELLED
        booking.save()

        with pytest.raises(ValidationError) as excinfo:
            Payment(booking=booking, amount=booking.total_amount).clean()
        assert "Нельзя оплатить отменённую или истекшую бронь" in str(excinfo.value)
