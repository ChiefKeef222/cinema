from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.movies.models import Movie
from apps.users.models import User
from apps.schedule.models import Hall, Session
from django.utils import timezone
from datetime import timedelta


class MovieAPITestCase(APITestCase):
    def setUp(self):
        # Создаём суперпользователя
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        # Создаём обычного пользователя
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )
        # Создаём фильм
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller",
            duration=148,
            poster_url="http://example.com/inception.jpg",
        )

    def test_get_movies_list(self):
        url = reverse("movie-list")  # имя роута в DRF SimpleRouter
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_movie_detail(self):
        url = reverse("movie-detail", kwargs={"public_id": self.movie.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Inception")

    def test_create_movie_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("movie-list")
        data = {
            "title": "Interstellar",
            "description": "Space exploration",
            "duration": 169,
            "poster_url": "http://example.com/interstellar.jpg",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_update_movie_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("movie-detail", kwargs={"public_id": self.movie.public_id})
        data = {"title": "Inception Updated"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "Inception Updated")

    def test_delete_movie_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("movie-detail", kwargs={"public_id": self.movie.public_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Movie.objects.filter(pk=self.movie.pk).exists())


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )

    def test_get_users_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_user_detail(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-detail", kwargs={"pk": self.user.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user1")


class HallAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )
        self.hall = Hall.objects.create(name="Зал 1", rows=10, seats_per_row=12)

    def test_get_halls_list(self):
        url = reverse("hall-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_hall_detail(self):
        url = reverse("hall-detail", kwargs={"public_id": self.hall.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Зал 1")

    def test_create_hall_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("hall-list")
        data = {"name": "Зал 2", "rows": 15, "seats_per_row": 20}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Зал успешно создан")
        self.assertIn("id", response.data)

    def test_create_hall_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("hall-list")
        data = {"name": "Зал 3", "rows": 8, "seats_per_row": 12}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_hall_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("hall-detail", kwargs={"public_id": self.hall.public_id})
        data = {"name": "Зал обновлён"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Зал успешно обновлён")
        self.hall.refresh_from_db()
        self.assertEqual(self.hall.name, "Зал обновлён")

    def test_delete_hall_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("hall-detail", kwargs={"public_id": self.hall.public_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Зал успешно удалён")
        self.assertFalse(Hall.objects.filter(pk=self.hall.pk).exists())


class SessionAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )
        self.hall = Hall.objects.create(name="Зал 1", rows=10, seats_per_row=12)
        self.movie = Movie.objects.create(
            title="Inception",
            description="Mind-bending thriller",
            duration=148,
            poster_url="http://example.com/inception.jpg",
        )
        self.session = Session.objects.create(
            hall_id=self.hall,
            movie_id=self.movie,
            start_time=timezone.now() + timedelta(hours=1),
            price=1500,
        )

    def test_get_sessions_list(self):
        url = reverse("session-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_session_detail(self):
        url = reverse("session-detail", kwargs={"public_id": self.session.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["price"]), 1500)

    def test_create_session_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("session-list")
        data = {
            "hall_id": str(self.hall.public_id),
            "movie_id": str(self.movie.public_id),
            "start_time": (timezone.now() + timedelta(hours=5)).isoformat(),
            "price": 2000,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Сеанс успешно создан")

    def test_create_session_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("session-list")
        data = {
            "hall_id": str(self.hall.public_id),
            "movie_id": str(self.movie.public_id),
            "start_time": (timezone.now() + timedelta(hours=5)).isoformat(),
            "price": 2000,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_session_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("session-detail", kwargs={"public_id": self.session.public_id})
        data = {"price": 1800}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Сеанс успешно обновлён")
        self.session.refresh_from_db()
        self.assertEqual(float(self.session.price), 1800)

    def test_delete_session_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("session-detail", kwargs={"public_id": self.session.public_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Сеанс успешно удалён")
        self.assertFalse(Session.objects.filter(pk=self.session.pk).exists())
