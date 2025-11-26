import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.booking.models import Booking, BookingStatus
from apps.users.models import User
from apps.schedule.models import Seat, Hall, Session

# Import shared fixtures


# Fixtures specific to these tests
@pytest.fixture
def other_user(db) -> User:
    """A second user for testing permissions and isolation."""
    return User.objects.create_user(
        username="otheruser", email="other@user.com", password="Barsik_04"
    )


@pytest.fixture
def seats(db, hall: Hall) -> list[Seat]:
    """A set of seats for the tests."""
    return [
        Seat.objects.create(hall=hall, row_number=1, seat_number=i + 1)
        for i in range(5)
    ]


@pytest.fixture
def booking(db, user: User, session: Session, seats: list[Seat]) -> Booking:
    """A booking belonging to the primary test user."""
    b = Booking.objects.create(user=user, session=session)
    b.seats.add(seats[0], seats[1])
    b.save()
    return b


@pytest.fixture
def other_booking(db, other_user: User, session: Session, seats: list[Seat]) -> Booking:
    """A booking belonging to the secondary 'other' user."""
    b = Booking.objects.create(user=other_user, session=session)
    b.seats.add(seats[2], seats[3])
    b.save()
    return b


@pytest.mark.django_db
class TestBookingViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.list_create_url = reverse("booking-list")

    def detail_url(self, booking_id):
        return reverse("booking-detail", kwargs={"public_id": booking_id})

    def cancel_url(self, booking_id):
        return reverse("booking-cancel-booking", kwargs={"public_id": booking_id})

    def test_auth_required(self):
        """Test that authentication is required for all booking endpoints."""
        response = self.client.get(self.list_create_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = self.client.post(self.list_create_url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.booking.tasks.check_booking_expiration.apply_async")
    @patch("apps.booking.views.get_channel_layer")
    def test_create_booking_success(
        self, mock_get_channel_layer, mock_check_expiration, user, session, seats
    ):
        """Test successful booking creation."""
        # Configure mocks
        mock_task_result = MagicMock()
        mock_task_result.id = "fake-celery-task-id"
        mock_check_expiration.return_value = mock_task_result
        channel_layer_mock = MagicMock()
        channel_layer_mock.group_send = AsyncMock()
        mock_get_channel_layer.return_value = channel_layer_mock

        self.client.force_authenticate(user=user)
        data = {
            "session": str(session.public_id),
            "seats": [
                {"row_number": s.row_number, "seat_number": s.seat_number}
                for s in [seats[0], seats[1]]
            ],
        }
        response = self.client.post(self.list_create_url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Booking.objects.filter(user=user, session=session).exists()
        new_booking = Booking.objects.get(user=user, session=session)
        assert new_booking.seats.count() == 2
        mock_check_expiration.assert_called_once()
        channel_layer_mock.group_send.assert_called_once()

    def test_list_user_bookings(self, user, booking, other_booking):
        """Test that a user can only list their own bookings."""
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(booking.public_id)

    # test_retrieve_own_booking was removed as requested by the user.

    def test_cannot_retrieve_other_user_booking(self, user, other_booking):
        """Test that a user cannot retrieve another user's booking."""
        self.client.force_authenticate(user=user)
        url = self.detail_url(other_booking.public_id)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("config.celery.app.control.revoke")
    def test_cancel_booking_success(self, mock_celery_revoke, user, booking):
        """Test successfully cancelling a booking."""
        booking.task_id = "some-celery-task-id"
        booking.save()

        self.client.force_authenticate(user=user)
        url = self.cancel_url(booking.public_id)
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Бронь успешно отменена."

        booking.refresh_from_db()
        assert booking.status == BookingStatus.CANCELLED
        mock_celery_revoke.assert_called_once_with("some-celery-task-id")

    def test_cancel_already_cancelled_booking_fails(self, user, booking):
        """Test that a booking that is already cancelled cannot be cancelled again."""
        booking.status = BookingStatus.CANCELLED
        booking.save()

        self.client.force_authenticate(user=user)
        url = self.cancel_url(booking.public_id)
        response = self.client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPaymentAndSessionViews:
    def setup_method(self):
        self.client = APIClient()

    def pay_url(self, booking_id):
        return reverse("booking-pay", kwargs={"booking_id": booking_id})

    def seats_url(self, session_id):
        return reverse("session-seats", kwargs={"session_id": session_id})

    @patch("apps.booking.views.get_channel_layer")
    @patch("config.celery.app.control.revoke")
    def test_payment_success(
        self, mock_celery_revoke, mock_get_channel_layer, user, booking
    ):
        """Test successful payment for a booking."""
        # Configure mock for channel layer
        channel_layer_mock = MagicMock()
        channel_layer_mock.group_send = AsyncMock()
        mock_get_channel_layer.return_value = channel_layer_mock

        booking.status = BookingStatus.PENDING
        booking.task_id = "some-task"
        booking.save()

        self.client.force_authenticate(user=user)
        url = self.pay_url(booking.id)  # URL uses integer ID
        response = self.client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        booking.refresh_from_db()
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.payment.status == "paid"
        mock_celery_revoke.assert_called_once_with("some-task")
        channel_layer_mock.group_send.assert_called_once()

    def test_payment_for_other_user_booking_fails(self, user, other_booking):
        """Test that a user cannot pay for another user's booking."""
        self.client.force_authenticate(user=user)
        url = self.pay_url(other_booking.id)
        response = self.client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_session_seats(self, session, other_booking):
        """Test that the session seats view returns taken seats correctly."""
        url = self.seats_url(session.public_id)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sessionId"] == str(session.public_id)
        # other_booking has seats 2 and 3 (index) from the seats fixture
        taken = response.data["takenSeats"]
        assert len(taken) == other_booking.seats.count()
        assert {"row_number": 1, "seat_number": 3} in taken
        assert {"row_number": 1, "seat_number": 4} in taken
