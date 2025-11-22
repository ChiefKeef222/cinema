import pytest
from apps.users.models import User


data_user = {
    "email": "arhat_test@gmail.com",
    "username": "arhat_test",
    "password": "Barsik_04",
}


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(**data_user)
