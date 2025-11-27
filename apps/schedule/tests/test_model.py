import pytest
from apps.schedule.models import Hall, Seat, Session


@pytest.mark.django_db
class TestScheduleModels:
    def test_hall_creation(self, hall: Hall):
        assert hall.name == "Main Hall"
        assert str(hall) == "Main Hall"

    def test_seat_creation(self, hall: Hall):
        seat = Seat.objects.create(hall=hall, row_number=1, seat_number=5)
        assert seat.hall == hall
        assert seat.row_number == 1
        assert seat.seat_number == 5
        assert str(seat) == f"Зал {hall.name}: ряд 1, место 5"

    def test_seat_creation_with_minimum_values(self, hall: Hall):
        seat = Seat.objects.create(hall=hall, row_number=1, seat_number=1)
        assert seat.row_number == 1
        assert seat.seat_number == 1

    def test_seat_str_representation(self, hall: Hall):
        seat = Seat.objects.create(hall=hall, row_number=3, seat_number=7)
        assert str(seat) == f"Зал {hall.name}: ряд 3, место 7"

    def test_session_creation(self, session: Session, movie, hall):
        assert session.movie == movie
        assert session.hall == hall
        assert session.price == 15.00
        assert (
            str(session)
            == f"{movie.title} — {hall.name} ({session.start_time:%d.%m %H:%M})"
        )

    def test_seat_unique_constraint(self, hall: Hall):
        Seat.objects.create(hall=hall, row_number=2, seat_number=10)
        with pytest.raises(Exception) as excinfo:
            Seat.objects.create(hall=hall, row_number=2, seat_number=10)
        assert "unique_hall_row_seat" in str(excinfo.value).lower()
