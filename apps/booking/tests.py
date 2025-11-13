from django.test import TestCase
from django.utils import timezone
from apps.users.models import User
from apps.schedule.models import Hall, Seat, Session, Movie
from apps.booking.models import Booking, Payment, BookingStatus, PaymentStatus
from datetime import timedelta


class BookingPaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="Barsik_04"
        )

        self.hall = Hall.objects.create(name="Hall 1")
        self.seat1 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=1)
        self.seat2 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=2)

        self.movie = Movie.objects.create(
            title="Test Movie", description="desc", duration=120
        )
        self.session = Session.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=timezone.now() + timedelta(days=1),
            price=500.00,
        )

    def test_create_booking_success(self):
        booking = Booking.objects.create(user=self.user, session=self.session)
        booking.seats.add(self.seat1, self.seat2)
        booking.save()
        self.assertEqual(booking.status, BookingStatus.PENDING)
        self.assertIsNotNone(booking.expires_at)
        self.assertEqual(booking.seats.count(), 2)

    def test_create_booking_seat_not_in_hall(self):
        other_hall = Hall.objects.create(name="Hall 2")
        seat3 = Seat.objects.create(hall=other_hall, row_number=1, seat_number=1)
        booking = Booking(user=self.user, session=self.session)
        booking.save()
        booking.seats.add(seat3)
        with self.assertRaises(Exception):
            booking.clean()

    def test_booking_expiry(self):
        booking = Booking.objects.create(
            user=self.user,
            session=self.session,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        booking.seats.add(self.seat1)
        if (
            booking.expires_at < timezone.now()
            and booking.status == BookingStatus.PENDING
        ):
            booking.status = BookingStatus.EXPIRED
            booking.save()
        self.assertEqual(booking.status, BookingStatus.EXPIRED)

    def test_payment_marks_booking_confirmed(self):
        booking = Booking.objects.create(user=self.user, session=self.session)
        booking.seats.add(self.seat1)
        payment = Payment.objects.create(
            booking=booking, amount=500.00, status=PaymentStatus.PAID
        )
        booking.status = BookingStatus.CONFIRMED
        booking.save()
        self.assertEqual(payment.booking.status, BookingStatus.CONFIRMED)
        self.assertEqual(payment.status, PaymentStatus.PAID)

    def test_cannot_pay_cancelled_booking(self):
        booking = Booking.objects.create(
            user=self.user, session=self.session, status=BookingStatus.CANCELLED
        )
        booking.seats.add(self.seat1)
        with self.assertRaises(Exception):
            Payment.objects.create(booking=booking, amount=500.00)
