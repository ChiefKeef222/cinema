from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.schedule.models import Session, Seat, Hall, Movie
from .models import Booking
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class BookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        # Фильм и зал
        self.movie = Movie.objects.create(title="Test Movie", duration=120)
        self.hall = Hall.objects.create(name="Test Hall")

        # Сеанс
        self.session = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=timezone.now() + timedelta(days=1),
            price=500
        )

        # Места
        self.seat1 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=1)
        self.seat2 = Seat.objects.create(hall=self.hall, row_number=1, seat_number=2)

    def test_create_booking_success(self):
        data = {
            "session": str(self.session.public_id),
            "seats": [
                {"row_number": 1, "seat_number": 1},
                {"row_number": 1, "seat_number": 2}
            ]
        }
        response = self.client.post("/api/booking/bookings/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.first().seats.count(), 2)

    def test_create_booking_already_taken(self):
        booking = Booking.objects.create(session=self.session, user=self.user)
        booking.seats.add(self.seat1)

        data = {
            "session": str(self.session.public_id),
            "seats": [
                {"row_number": 1, "seat_number": 1},
                {"row_number": 1, "seat_number": 2}
            ]
        }
        response = self.client.post("/api/booking/bookings/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("taken", response.data)

    def test_get_user_bookings(self):
        booking = Booking.objects.create(session=self.session, user=self.user)
        booking.seats.add(self.seat1)

        response = self.client.get("/api/booking/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["seats"][0]["row_number"], 1)

    def test_get_taken_seats_for_session(self):
        booking = Booking.objects.create(session=self.session, user=self.user)
        booking.seats.add(self.seat1, self.seat2)

        client = APIClient()  # Неавторизованный клиент
        response = client.get(f"/api/booking/sessions/{self.session.public_id}/seats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["takenSeats"]), 2)
        self.assertEqual(response.data["takenSeats"][0]["row"], 1)
        self.assertEqual(response.data["takenSeats"][0]["seat"], 1)
