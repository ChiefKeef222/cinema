import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta
import zoneinfo

from apps.schedule.models import Hall, Session
from apps.movies.models import Movie


@pytest.mark.django_db
class TestHallViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.list_create_endpoint = reverse("hall-list")

    def get_detail_endpoint(self, public_id):
        return reverse("hall-detail", kwargs={"public_id": public_id})

    def test_list_halls(self, user, hall):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        assert response.data["results"][0]["name"] == hall.name

    def test_retrieve_hall(self, user, hall):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(hall.public_id)
        response = self.client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(hall.public_id)
        assert response.data["name"] == hall.name

    def test_retrieve_hall_with_seats(self, user, hall):
        self.client.force_authenticate(user=user)
        # Create seats for the hall
        from apps.schedule.models import Seat

        Seat.objects.create(hall=hall, row_number=1, seat_number=1)
        Seat.objects.create(hall=hall, row_number=1, seat_number=2)

        endpoint = self.get_detail_endpoint(hall.public_id)
        response = self.client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["seats"]) == 2
        assert response.data["seats"][0]["row_number"] == 1
        assert response.data["seats"][0]["seat_number"] == 1

    def test_list_halls_empty(self, user):
        # Ensure no halls exist other than the ones created by fixtures for this test run
        Hall.objects.all().delete()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_create_hall_by_superuser(self, superuser):
        self.client.force_authenticate(user=superuser)
        data = {
            "name": "Small Hall",
            "rows": [
                {"row_number": 1, "seats": 5},
                {"row_number": 2, "seats": 8},
            ],
        }
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Verify hall and seats were created
        new_hall = Hall.objects.get(name="Small Hall")
        assert new_hall.seats.count() == 13  # 5 + 8

    def test_update_hall_by_superuser(self, superuser, hall):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(hall.public_id)
        updated_name = "Updated Main Hall"
        data = {
            "name": updated_name,
            "rows": [  # rows field is write_only, so it must be provided for update too if we want to change it.
                {"row_number": 1, "seats": 5},
                {"row_number": 2, "seats": 5},
            ],
        }
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        hall.refresh_from_db()
        assert hall.name == updated_name
        assert hall.seats.count() == 10  # 5 + 5

    def test_partial_update_hall_by_superuser(self, superuser, hall):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(hall.public_id)
        updated_name = "Partially Updated Hall"
        data = {"name": updated_name}  # Only updating name
        response = self.client.patch(endpoint, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        hall.refresh_from_db()
        assert hall.name == updated_name
        # Seats should remain unchanged for partial update unless 'rows' is provided

    def test_create_hall_by_user_fails(self, user):
        self.client.force_authenticate(user=user)
        data = {"name": "Another Hall", "rows": []}
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_hall_by_user_fails(self, user, hall):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(hall.public_id)
        data = {"name": "Attempt to update"}
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_hall_by_superuser(self, superuser, hall):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(hall.public_id)
        response = self.client.delete(endpoint)
        assert (
            response.status_code == status.HTTP_200_OK
        )  # Custom implementation returns 200
        assert not Hall.objects.filter(pk=hall.pk).exists()

    def test_unauthenticated_list_halls_fails(self):
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_retrieve_hall_fails(self, hall):
        endpoint = self.get_detail_endpoint(hall.public_id)
        response = self.client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_create_hall_fails(self):
        data = {"name": "Unauthenticated Hall", "rows": []}
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_update_hall_fails(self, hall):
        endpoint = self.get_detail_endpoint(hall.public_id)
        data = {"name": "Unauthenticated Update"}
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_delete_hall_fails(self, hall):
        endpoint = self.get_detail_endpoint(hall.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSessionViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.list_create_endpoint = reverse("session-list")

    def get_detail_endpoint(self, public_id):
        return reverse("session-detail", kwargs={"public_id": public_id})

    def test_list_sessions(self, user, session):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        assert response.data["results"][0]["id"] == str(session.public_id)

    def test_retrieve_session(self, user, session):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(session.public_id)
        response = self.client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["movie"]) == str(session.movie.public_id)
        assert str(response.data["hall"]) == str(session.hall.public_id)

    def test_list_sessions_empty(self, user):
        Session.objects.all().delete()  # Clear existing sessions
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_create_session_by_superuser(self, superuser, movie, hall):
        self.client.force_authenticate(user=superuser)
        utc_tz = zoneinfo.ZoneInfo("UTC")
        start_time = datetime.now(utc_tz) + timedelta(days=1)
        data = {
            "movie": str(movie.public_id),
            "hall": str(hall.public_id),
            "start_time": start_time.isoformat(),
            "price": 25.50,
        }
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        new_session = Session.objects.get(public_id=response.data["id"])
        assert new_session.movie == movie
        assert new_session.hall == hall

    def test_update_session_by_superuser(self, superuser, session, movie, hall):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(session.public_id)
        updated_price = 30.00
        utc_tz = zoneinfo.ZoneInfo("UTC")
        new_start_time = datetime.now(utc_tz) + timedelta(days=2)
        data = {
            "movie": str(movie.public_id),
            "hall": str(hall.public_id),
            "start_time": new_start_time.isoformat(),
            "price": updated_price,
        }
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        session.refresh_from_db()
        assert session.price == updated_price
        assert session.start_time.isoformat() == new_start_time.isoformat()

    def test_partial_update_session_by_superuser(self, superuser, session):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(session.public_id)
        updated_price = 35.00
        data = {"price": updated_price}
        response = self.client.patch(endpoint, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        session.refresh_from_db()
        assert session.price == updated_price

    def test_delete_session_by_superuser(self, superuser, session):
        self.client.force_authenticate(user=superuser)
        endpoint = self.get_detail_endpoint(session.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert not Session.objects.filter(pk=session.pk).exists()

    def test_create_session_by_user_fails(self, user, movie, hall):
        self.client.force_authenticate(user=user)
        utc_tz = zoneinfo.ZoneInfo("UTC")
        start_time = datetime.now(utc_tz) + timedelta(days=1)
        data = {
            "movie": str(movie.public_id),
            "hall": str(hall.public_id),
            "start_time": start_time.isoformat(),
            "price": 25.50,
        }
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_session_by_user_fails(self, user, session):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(session.public_id)
        data = {"price": 99.99}
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_session_by_user_fails(self, user, session):
        self.client.force_authenticate(user=user)
        endpoint = self.get_detail_endpoint(session.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_session_by_movie(self, user, session, movie):
        self.client.force_authenticate(user=user)
        # Create another session with a different movie to ensure filtering works
        other_movie = Movie.objects.create(title="Another Movie", duration=90)
        Session.objects.create(
            movie=other_movie,
            hall=session.hall,
            start_time=session.start_time + timedelta(hours=1),
            price=session.price,
        )

        response = self.client.get(
            self.list_create_endpoint, {"movie": movie.public_id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(session.public_id)

    def test_filter_session_by_hall(self, user, session, movie, hall):
        self.client.force_authenticate(user=user)

        other_hall = Hall.objects.create(name="Other Hall")
        Session.objects.create(
            movie=movie,
            hall=other_hall,
            start_time=session.start_time + timedelta(hours=1),
            price=session.price,
        )

        response = self.client.get(self.list_create_endpoint, {"hall": hall.public_id})

        assert response.status_code == status.HTTP_200_OK

        # пагинация: данные лежат в "results"
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        item = response.data["results"][0]
        assert item["hall"] == hall.public_id
        assert item["movie"] == movie.public_id

    def test_filter_session_by_date(self, user, session):
        self.client.force_authenticate(user=user)
        Session.objects.create(
            movie=session.movie,
            hall=session.hall,
            start_time=session.start_time + timedelta(days=6),
            price=session.price,
        )

        date_str = session.start_time.strftime("%Y-%m-%d")
        response = self.client.get(self.list_create_endpoint, {"date": date_str})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_session_by_invalid_uuid(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint, {"movie": "invalid-uuid"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Параметр 'movie' должен быть UUID." in response.data["detail"]

        response = self.client.get(self.list_create_endpoint, {"hall": "invalid-uuid"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Параметр 'hall' должен быть UUID." in response.data["detail"]

    def test_filter_session_by_invalid_date_format(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_endpoint, {"date": "invalid-date"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный формат даты" in response.data["detail"]

    def test_unauthenticated_list_sessions_fails(self):
        response = self.client.get(self.list_create_endpoint)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_retrieve_session_fails(self, session):
        endpoint = self.get_detail_endpoint(session.public_id)
        response = self.client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_create_session_fails(self, movie, hall):
        utc_tz = zoneinfo.ZoneInfo("UTC")
        start_time = datetime.now(utc_tz) + timedelta(days=1)
        data = {
            "movie": str(movie.public_id),
            "hall": str(hall.public_id),
            "start_time": start_time.isoformat(),
            "price": 25.50,
        }
        response = self.client.post(self.list_create_endpoint, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_update_session_fails(self, session):
        endpoint = self.get_detail_endpoint(session.public_id)
        data = {"price": 99.99}
        response = self.client.put(endpoint, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_delete_session_fails(self, session):
        endpoint = self.get_detail_endpoint(session.public_id)
        response = self.client.delete(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
