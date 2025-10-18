from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User  # твой кастомный User
from apps.movies.models import Movie
from apps.schedule.models import Hall, Session
from datetime import datetime, timedelta
import pytz
from datetime import date


tz = pytz.timezone("Asia/Almaty")  # UTC+5
today_local = datetime.now(tz).date()


class HallCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_hall(self):
        data = {
            "name": "Hall A",
            "rows": [{"row_number": 1, "seats": 5}, {"row_number": 2, "seats": 5}],
        }
        response = self.client.post("/api/schedule/halls/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_list_halls(self):
        hall = Hall.objects.create(name="Hall B")
        response = self.client.get("/api/schedule/halls/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(h["id"] == str(hall.public_id) for h in response.data))

    def test_retrieve_hall(self):
        hall = Hall.objects.create(name="Hall C")
        response = self.client.get(f"/api/schedule/halls/{hall.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(hall.public_id))

    def test_update_hall(self):
        hall = Hall.objects.create(name="Hall D")
        data = {"name": "Hall D Updated"}
        response = self.client.patch(
            f"/api/schedule/halls/{hall.public_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hall.refresh_from_db()
        self.assertEqual(hall.name, "Hall D Updated")

    def test_delete_hall(self):
        hall = Hall.objects.create(name="Hall E")
        response = self.client.delete(f"/api/schedule/halls/{hall.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Hall.objects.filter(id=hall.id).exists())

    def test_list_halls_no_results(self):
        Hall.objects.all().delete()

        response = self.client.get("/api/schedule/halls/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class SessionCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.client.force_authenticate(user=self.admin)

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            duration=120,
            poster_url="http://example.com/poster.jpg",
        )
        self.hall = Hall.objects.create(name="Hall 1")

        # Добавляем ряды и места
        for r in range(1, 3):
            for s in range(1, 6):
                self.hall.seats.create(row_number=r, seat_number=s)

    def test_create_session(self):
        data = {
            "movie_id": str(self.movie.public_id),
            "hall_id": str(self.hall.public_id),
            "start_time": (datetime.now(pytz.UTC) + timedelta(days=1)).isoformat(),
            "price": "2500.00",
        }
        response = self.client.post("/api/schedule/sessions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_list_sessions(self):
        session = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=datetime.now(pytz.UTC) + timedelta(days=1),
            price="2500.00",
        )
        response = self.client.get("/api/schedule/sessions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(s["id"] == str(session.public_id) for s in response.data))

    def test_retrieve_session(self):
        session = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=datetime.now(pytz.UTC) + timedelta(days=1),
            price="2500.00",
        )
        response = self.client.get(f"/api/schedule/sessions/{session.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(session.public_id))

    def test_update_session(self):
        session = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=datetime.now(pytz.UTC) + timedelta(days=1),
            price="2500.00",
        )
        data = {"price": "2700.00"}
        response = self.client.patch(
            f"/api/schedule/sessions/{session.public_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(str(session.price), "2700.00")

    def test_delete_session(self):
        session = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=datetime.now(pytz.UTC) + timedelta(days=1),
            price="2500.00",
        )
        response = self.client.delete(f"/api/schedule/sessions/{session.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Session.objects.filter(id=session.id).exists())

    def test_filter_sessions(self):
        today = datetime.now(pytz.UTC)
        session1 = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=datetime.combine(today_local, datetime.min.time(), tzinfo=tz),
            price="2500.00",
        )

        session2 = Session.objects.create(
            movie_id=self.movie,
            hall_id=self.hall,
            start_time=today + timedelta(days=1),
            price="2500.00",
        )
        response = self.client.get(
            "/api/schedule/sessions/", {"date": today.date().isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(session1.public_id))

    def test_filter_sessions_no_results(self):
        Session.objects.all().delete()

        response = self.client.get("/api/schedule/sessions/", {"date": "2100-01-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_filter_session_invalid_uuid(self):
        response = self.client.get("/api/schedule/sessions/", {"movie": "123"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("UUID", str(response.data))
