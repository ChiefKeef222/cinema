from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from apps.users.models import User


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )

    def test_register_user_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123",
        }

        response = self.client.post(reverse("auth-register-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "newuser@example.com")

        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_user_invalid_data(self):
        data = {"username": "no_password", "email": "no_password@example.com"}

        response = self.client.post(reverse("auth-register-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Обязательное поле", response.data["error"])

    def test_login_user_success(self):
        data = {"email": "user1@example.com", "password": "password123"}
        response = self.client.post(reverse("auth-login-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "user1@example.com")

    def test_login_invalid_credentials(self):
        data = {"email": "user1@example.com", "password": "wrongpass"}
        response = self.client.post(reverse("auth-login-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Не найдено активной учетной записи с указанными данными",
        )

    def test_refresh_token_success(self):
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}

        response = self.client.post(reverse("auth-refresh-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        data = {"refresh": "invalid_token"}
        response = self.client.post(reverse("auth-refresh-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Token is invalid")
