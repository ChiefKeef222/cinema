from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from movies.models import Movie
from users.models import User


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
