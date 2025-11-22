import pytest
from apps.users.models import User


data_user = {
    "username": "test_user",
    "email": "test@gmail.com",
    "password": "Strong_password",
}


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(**data_user)
    assert user.username == data_user["username"]
    assert user.email == data_user["email"]


data_superuser = {
    "username": "test_superuser",
    "email": "testsuperuser@gmail.com",
    "password": "Test_superpassword",
}


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(**data_superuser)
    assert user.username == data_superuser["username"]
    assert user.email == data_superuser["email"]
    assert user.is_superuser == user.is_superuser
    assert user.is_staff == user.is_staff
