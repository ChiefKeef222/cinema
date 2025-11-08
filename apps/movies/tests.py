from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.movies.models import Movie
from apps.users.models import User


class MovieCRUDTests(TestCase):
    def setUp(self):
        self.movie_data = {
            "title": "Test Movie",
            "description": "Описание тестового фильма",
            "duration": 120,
            "poster_url": "http://example.com/poster.jpg",
        }
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", password="04091998Aa", email="admin@example.com"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_movie(self):
        response = self.client.post("/api/movies/", self.movie_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertTrue(Movie.objects.filter(title="Test Movie").exists())

    def test_list_movies(self):
        Movie.objects.create(**self.movie_data)
        self.client.force_authenticate(user=None)  # проверяем публичный доступ
        response = self.client.get("/api/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Movie")

    def test_retrieve_movie(self):
        movie = Movie.objects.create(**self.movie_data)
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/api/movies/{movie.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], movie.title)

    def test_update_movie(self):
        movie = Movie.objects.create(**self.movie_data)
        updated_data = {**self.movie_data, "title": "Updated Movie"}
        response = self.client.put(
            f"/api/movies/{movie.public_id}/", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        self.assertEqual(movie.title, "Updated Movie")

    def test_delete_movie(self):
        movie = Movie.objects.create(**self.movie_data)
        response = self.client.delete(f"/api/movies/{movie.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Movie.objects.filter(public_id=movie.public_id).exists())

    def test_search_movie(self):
        Movie.objects.all().delete()
        Movie.objects.create(
            title="Avengers",
            description="Hero movie",
            duration=120,
            poster_url="http://example.com/1.jpg",
        )
        Movie.objects.create(
            title="Inception",
            description="Dream movie",
            duration=150,
            poster_url="http://example.com/2.jpg",
        )
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/movies/?search=Avengers")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Avengers")

    def test_search_movie_too_long(self):
        long_title = "a" * 101
        response = self.client.get("/api/movies/", {"search": long_title})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Параметр поиска не может быть длиннее 100 символов", str(response.data)
        )
