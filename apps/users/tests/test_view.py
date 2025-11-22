import pytest
from rest_framework import status


class TestAuthenticationViewSet:
    endpoint = "/api/auth/"

    def test_login(self, client, user):
        data = {"email": user.email, "password": "Barsik_04"}
        response = client.post(self.endpoint + "login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["access"]
        assert response.data["user"]["id"] == str(user.public_id)
        assert response.data["user"]["username"] == user.username
        assert response.data["user"]["email"] == user.email

    @pytest.mark.django_db
    def test_register(self, client):
        data = {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "test_password",
        }

        response = client.post(self.endpoint + "register/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_refresh_token(self, client, user):
        data = {"email": user.email, "password": "Barsik_04"}
        response = client.post(self.endpoint + "login/", data)
        assert response.status_code == status.HTTP_200_OK

        data_refresh = {"refresh": response.data["refresh"]}

        response = client.post(self.endpoint + "refresh/", data_refresh)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["access"]
