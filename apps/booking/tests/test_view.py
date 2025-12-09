import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.booking.models import Booking, BookingStatus
from apps.users.models import User
from apps.schedule.models import Seat, Hall, Session


@pytest.fixture
def other_user(db) -> User:
    return User.objects.create_user(
        username="otheruser", email="other@user.com", password="Barsik_04"
    )


@pytest.fixture
def seats(db, hall: Hall) -> list[Seat]:
    return [
        Seat.objects.create(hall=hall, row_number=1, seat_number=i + 1)
        for i in range(5)
    ]


@pytest.fixture
def booking(db, user: User, session: Session, seats: list[Seat]) -> Booking:
    b = Booking.objects.create(user=user, session=session)
    b.seats.add(seats[0], seats[1])
    b.save()
    return b


@pytest.fixture
def other_booking(db, other_user: User, session: Session, seats: list[Seat]) -> Booking:
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
        response = self.client.get(self.list_create_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = self.client.post(self.list_create_url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.booking.tasks.check_booking_expiration.apply_async")
    @patch("apps.booking.views.get_channel_layer")
    def test_create_booking_success(
        self, mock_get_channel_layer, mock_check_expiration, user, session, seats
    ):
        mock_check_expiration.return_value = MagicMock(id="fake-celery-task-id")
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
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(booking.public_id)

    def test_cannot_retrieve_other_user_booking(self, user, other_booking):
        self.client.force_authenticate(user=user)
        url = self.detail_url(other_booking.public_id)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("config.celery.app.control.revoke")
    def test_cancel_booking_success(self, mock_celery_revoke, user, booking):
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
        booking.status = BookingStatus.CANCELLED
        booking.save()

        self.client.force_authenticate(user=user)
        url = self.cancel_url(booking.public_id)
        response = self.client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    #
    # @patch("apps.booking.tasks.check_booking_expiration.apply_async")
    # @patch("apps.booking.views.get_channel_layer")
    # def test_create_booking_throttling(
    #         self,
    #         mock_get_channel_layer,
    #         mock_check_expiration,
    #         user,
    #         session,
    #         seats,
    # ):
    #     mock_check_expiration.return_value = MagicMock(id="fake-celery-task-id") # FIX
    #     channel_layer_mock = MagicMock()
    #     channel_layer_mock.group_send = AsyncMock()
    #     mock_get_channel_layer.return_value = channel_layer_mock
    #
    #     self.client.force_authenticate(user=user)
    #     data = {
    #         "session": str(session.public_id),
    #         "seats": [
    #             {
    #                 "row_number": s.row_number,
    #                 "seat_number": s.seat_number,
    #             }
    #             for s in [seats[0]]
    #         ],
    #     }
    #     response1 = self.client.post(self.list_create_url, data, format="json")
    #     assert response1.status_code == status.HTTP_201_CREATED
    #
    #     data["seats"] = [
    #         {
    #             "row_number": s.row_number,
    #             "seat_number": s.seat_number,
    #         }
    #         for s in [seats[1]]
    #     ]
    #     response2 = self.client.post(self.list_create_url, data, format="json")
    #     assert response2.status_code == status.HTTP_201_CREATED
    #
    #     data["seats"] = [
    #         {
    #             "row_number": s.row_number,
    #             "seat_number": s.seat_number,
    #         }
    #         for s in [seats[2]]
    #     ]
    #     response3 = self.client.post(self.list_create_url, data, format="json")
    #     assert response3.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    #     assert "Request was throttled" in response3.data["detail"]
    #
    # @patch("apps.booking.views.BookingViewSet.perform_create")
    # @patch("logging.getLogger")
    # def test_internal_server_error_logs_correctly(
    #         self,
    #         mock_get_logger,
    #         mock_perform_create,
    #         user,
    #         session,
    #         seats,
    # ):
    #     mock_perform_create.side_effect = Exception("Simulated internal server error")
    #     mock_logger = MagicMock()
    #     mock_get_logger.return_value = mock_logger
    #
    #     self.client.force_authenticate(user=user)
    #     data = {
    #         "session": str(session.public_id),
    #         "seats": [
    #             {
    #                 "row_number": s.row_number,
    #                 "seat_number": s.seat_number,
    #             }
    #             for s in [seats[0]]
    #         ],
    #     }
    #     response = self.client.post(self.list_create_url, data, format="json")
    #
    #     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    #     mock_logger.error.assert_called_once()
    #     assert "Simulated internal server error" in mock_logger.error.call_args[0][0] # More specific log message check if needed

    # @patch("apps.booking.tasks.check_booking_expiration.apply_async")
    # @patch("apps.booking.views.get_channel_layer")
    # def test_create_booking_with_invalid_data_fails(
    #         self,
    #         mock_get_channel_layer,
    #         mock_check_expiration,
    #         user,
    #         session,
    #         seats,
    # ):
    # mock_check_expiration.return_value = MagicMock(id="fake-celery-task-id") # FIX
    # self.client.force_authenticate(user=user)
    #  Отсутствует обязательное поле 'session'
    # data = {
    #     "seats": [
    #         {
    #             "row_number": s.row_number,
    #             "seat_number": s.seat_number,
    #         }
    #         for s in [seats[0], seats[1]]
    #     ],
    # }
    # response = self.client.post(self.list_create_url, data, format="json")
    # assert response.status_code == status.HTTP_400_BAD_REQUEST
    # assert "session" in response.data
    # assert "This field is required." in response.data["session"]
    # mock_check_expiration.assert_not_called()
    # mock_get_channel_layer.assert_not_called()

    def pay_url(self, booking_id):
        return reverse("booking-pay", kwargs={"booking_id": booking_id})

    def seats_url(self, session_id):
        return reverse("session-seats", kwargs={"session_id": session_id})

    @patch("apps.booking.views.get_channel_layer")
    @patch("config.celery.app.control.revoke")
    def test_payment_success(
        self, mock_celery_revoke, mock_get_channel_layer, user, booking
    ):
        channel_layer_mock = MagicMock()
        channel_layer_mock.group_send = AsyncMock()
        mock_get_channel_layer.return_value = channel_layer_mock

        booking.status = BookingStatus.PENDING
        booking.task_id = "some-task"
        booking.save()

        self.client.force_authenticate(user=user)
        url = self.pay_url(booking.public_id)
        response = self.client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        booking.refresh_from_db()
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.payment.status == "paid"
        mock_celery_revoke.assert_called_once_with("some-task")
        channel_layer_mock.group_send.assert_called_once()

    def test_payment_for_other_user_booking_fails(self, user, other_booking):
        self.client.force_authenticate(user=user)
        url = self.pay_url(other_booking.public_id)
        response = self.client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_session_seats(self, session, other_booking):
        url = self.seats_url(session.public_id)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sessionId"] == str(session.public_id)
        taken = response.data["takenSeats"]
        assert len(taken) == other_booking.seats.count()
        assert {"row_number": 1, "seat_number": 3} in taken
        assert {"row_number": 1, "seat_number": 4} in taken
