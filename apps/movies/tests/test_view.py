import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestMovieViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.list_create_endpoint = reverse("movie-list")

    def get_detail_endpoint(self, public_id):
        return reverse("movie-detail", kwargs={"public_id": public_id})

    def test_list_movies_authenticated(self, user, movie):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        assert response.data["results"][0]["title"] == movie.title

    def test_create_movie_by_regular_user_fails(self, user):
        self.client.force_authenticate(user=user)
        data = {
            "title": "New Movie (2023)",
            "description": "A new film.",
            "duration": 120,
            "poster_url": "https://example.com/poster.jpg",
        }
        response = self.client.post(self.list_create_endpoint, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_movie_by_superuser_succeeds(self, superuser):
        self.client.force_authenticate(user=superuser)
        data = {
            "title": "Super Movie (2023)",
            "description": "A super film.",
            "duration": 150,
            "poster_url": "https://example.com/super_poster.jpg",
        }
        response = self.client.post(self.list_create_endpoint, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert "id" in response.data

    def test_retrieve_movie_succeeds(self, user, movie):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(movie.public_id)
        response = self.client.get(endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(movie.public_id)
        assert response.data["title"] == movie.title

    def test_partial_update_movie_by_regular_user_fails(self, movie, user):
        self.client.force_authenticate(user=user)
        data = {"title": "The Updated Title"}
        endpoint = self.get_detail_endpoint(movie.public_id)
        response = self.client.patch(endpoint, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_movie_by_superuser_succeeds(self, movie, superuser):
        self.client.force_authenticate(user=superuser)
        data = {"title": "The Super Updated Title"}
        endpoint = self.get_detail_endpoint(movie.public_id)
        response = self.client.patch(endpoint, data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

        movie.refresh_from_db()
        assert movie.title == data["title"]

    def test_delete_movie_by_regular_user_fails(self, movie, user):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(movie.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_movie_by_superuser_succeeds(self, movie, superuser):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(movie.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

        assert not type(movie).objects.filter(pk=movie.pk).exists()
