import pytest
from datetime import datetime, timedelta, timezone
import zoneinfo
from rest_framework.exceptions import ValidationError

from apps.schedule.serializer import HallSerializer, SessionSerializer
from apps.schedule.models import Hall, Seat, Session
from apps.movies.models import Movie


@pytest.mark.django_db
class TestHallSerializer:
    def test_create_hall_with_seats(self):
        data = {
            "name": "Test Hall with Seats",
            "rows": [
                {"row_number": 1, "seats": 3},
                {"row_number": 2, "seats": 2},
            ],
        }
        serializer = HallSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        hall = serializer.save()

        assert Hall.objects.count() == 1
        assert hall.name == "Test Hall with Seats"
        assert hall.seats.count() == 5

        seats = hall.seats.all().order_by("row_number", "seat_number")
        assert seats[0].row_number == 1
        assert seats[0].seat_number == 1
        assert seats[2].row_number == 1
        assert seats[2].seat_number == 3
        assert seats[3].row_number == 2
        assert seats[3].seat_number == 1
        assert seats[4].row_number == 2
        assert seats[4].seat_number == 2

    def test_create_hall_without_rows_fails(self):
        data = {
            "name": "Hall without Rows",
            "rows": [],
        }
        serializer = HallSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert "Rows list cannot be empty." in str(excinfo.value)

    def test_create_hall_with_invalid_row_data_fails(self):
        data = {
            "name": "Hall with Invalid Rows",
            "rows": [
                {"row_number": 1, "seats": 0},
            ],
        }
        serializer = HallSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert "Seats count must be greater than zero." in str(excinfo.value)

        data = {
            "name": "Hall with Missing Seats",
            "rows": [
                {"row_number": 1},
            ],
        }
        serializer = HallSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert "Seats count is required." in str(excinfo.value)

    def test_hall_serialization(self, hall: Hall):
        Seat.objects.create(hall=hall, row_number=1, seat_number=1)
        Seat.objects.create(hall=hall, row_number=1, seat_number=2)

        serializer = HallSerializer(instance=hall)
        data = serializer.data

        assert data["id"] == str(hall.public_id)
        assert data["name"] == hall.name
        assert len(data["seats"]) == 2
        assert data["seats"][0]["row_number"] == 1
        assert data["seats"][0]["seat_number"] == 1


@pytest.mark.django_db
class TestSessionSerializer:
    def test_create_session(self, movie: Movie, hall: Hall):
        almaty_tz = zoneinfo.ZoneInfo("Asia/Almaty")
        start_time = datetime.now(almaty_tz) + timedelta(hours=1)

        data = {
            "movie": str(movie.public_id),
            "hall": str(hall.public_id),
            "start_time": start_time.isoformat(),
            "price": "12.50",
        }

        serializer = SessionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        assert Session.objects.count() == 1
        assert session.movie == movie
        assert session.hall == hall
        assert session.start_time.isoformat() == start_time.isoformat()
        assert str(session.price) == "12.50"

    def test_create_session_with_nonexistent_movie_fails(self, hall: Hall):
        almaty_tz = zoneinfo.ZoneInfo("Asia/Almaty")
        start_time = datetime.now(almaty_tz) + timedelta(hours=1)

        data = {
            "movie": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "hall": str(hall.public_id),
            "start_time": start_time.isoformat(),
            "price": "10.00",
        }

        serializer = SessionSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert (
            "Объект с public_id=a1b2c3d4-e5f6-7890-1234-567890abcdef не существует."
            in str(excinfo.value)
        )

    def test_create_session_with_nonexistent_hall_fails(self, movie: Movie):
        almaty_tz = zoneinfo.ZoneInfo("Asia/Almaty")
        start_time = datetime.now(almaty_tz) + timedelta(hours=1)

        data = {
            "movie": str(movie.public_id),
            "hall": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "start_time": start_time.isoformat(),
            "price": "10.00",
        }

        serializer = SessionSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert (
            "Объект с public_id=a1b2c3d4-e5f6-7890-1234-567890abcdef не существует."
            in str(excinfo.value)
        )

    def test_session_serialization(self, session: Session, movie: Movie, hall: Hall):
        serializer = SessionSerializer(instance=session)
        data = serializer.data

        assert data["id"] == str(session.public_id)
        assert data["movie"] == movie.public_id
        assert data["hall"] == hall.public_id

        parsed = datetime.fromisoformat(data["start_time"])

        start_utc = parsed.astimezone(timezone.utc)
        session_utc = session.start_time.astimezone(timezone.utc)

        assert start_utc == session_utc

        assert float(data["price"]) == float(session.price)
