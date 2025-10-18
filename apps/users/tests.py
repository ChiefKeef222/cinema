from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )

    def test_get_users_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_user_detail(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-detail", kwargs={"pk": self.user.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user1")
