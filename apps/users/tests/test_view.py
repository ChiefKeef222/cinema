import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAuthenticationViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse("auth-login-list")
        self.register_url = reverse("auth-register-list")
        self.refresh_url = reverse("auth-refresh-list")

    def test_register_successfully(self):
        """
        Tests that a user can be registered successfully.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == data["email"]

    def test_login_successfully(self, user):
        """
        Tests that a previously created user can log in.
        Note: The password is taken from the 'user' fixture definition.
        """
        data = {"email": user.email, "password": "Barsik_04"}
        response = self.client.post(self.login_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["id"] == str(user.public_id)
        assert response.data["user"]["username"] == user.username
        assert response.data["user"]["email"] == user.email

    def test_login_with_wrong_password_fails(self, user):
        """
        Tests that login fails with an incorrect password.
        """
        data = {"email": user.email, "password": "WrongPassword"}
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_successfully(self, user):
        """
        Tests that a refresh token can be used to obtain a new access token.
        """
        # First, log in to get a refresh token
        login_data = {"email": user.email, "password": "Barsik_04"}
        login_response = self.client.post(self.login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data["refresh"]

        # Now, use the refresh token
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(self.refresh_url, refresh_data)

        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access" in refresh_response.data
        # The refresh token itself might be rotated, but the response should not contain the refresh token
        # unless configured to do so (e.g., with REFRESH_TOKEN_ROTATE = True).
        # We just care that we get a new access token.
