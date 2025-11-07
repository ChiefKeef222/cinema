from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime, timedelta
import pytz
from django.utils import timezone

from apps.movies.models import Movie
from apps.users.models import User
from apps.schedule.models import Hall, Session, Seat
from apps.booking.models import Booking


class BookingViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", username="user", password="test123"
        )

        self.hall = Hall.objects.create(name="Main Hall")

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Описание тестового фильма",
            duration=120,
            poster_url="http://example.com/poster.jpg",
        )

        self.session = Session.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=timezone.now() + timedelta(days=1),
            price="2500.00",
        )

        self.seat1 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=1)
        self.seat2 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=2)

    def test_create_booking_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("booking-list")
        data = {
            "session": str(self.session.public_id),
            "seats": [
                {"row_number": 1, "seat_number": 1},
                {"row_number": 1, "seat_number": 2},
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("booking_id", response.data)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.first()
        self.assertEqual(booking.seats.count(), 2)
        self.assertEqual(booking.user, self.user)

    def test_booking_already_taken_seat(self):
        self.client.force_authenticate(user=self.user)
        booking = Booking.objects.create(user=self.user, session=self.session)
        booking.seats.add(self.seat1)

        url = reverse("booking-list")
        data = {
            "session": str(self.session.public_id),
            "seats": [{"row_number": 1, "seat_number": 1}],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Некоторые места уже заняты", response.data["error"])
        self.assertIn("taken", response.data)

    def test_get_user_bookings(self):
        self.client.force_authenticate(user=self.user)
        booking = Booking.objects.create(user=self.user, session=self.session)
        booking.seats.add(self.seat1)

        url = reverse("booking-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["session"], str(self.session.public_id))

    def test_get_taken_seats_for_session(self):
        booking = Booking.objects.create(user=self.user, session=self.session)
        booking.seats.add(self.seat1)

        url = reverse("session-seats", args=[self.session.public_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("takenSeats", response.data)
        self.assertEqual(len(response.data["takenSeats"]), 1)
        self.assertEqual(response.data["takenSeats"][0]["row"], 1)
        self.assertEqual(response.data["takenSeats"][0]["seat"], 1)

    def test_create_booking_unauthenticated_user_forbidden(self):
        url = reverse("booking-list")
        data = {
            "session": str(self.session.public_id),
            "seats": [
                {"row_number": 1, "seat_number": 1},
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"].lower(), "authentication credentials were not provided.")
        self.assertEqual(Booking.objects.count(), 0)