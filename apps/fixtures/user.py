import pytest
from django.contrib.auth import get_user_model

# Using get_user_model is a more robust way to get the User model in Django projects
User = get_user_model()


data_user = {
    "email": "arhat_test@gmail.com",
    "username": "arhat_test",
    "password": "Barsik_04",
}

data_superuser = {
    "email": "arhat_superuser@gmail.com",
    "username": "arhat_superuser",
    "password": "Barsik_04",
}


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(**data_user)


@pytest.fixture
def superuser(db) -> User:
    return User.objects.create_superuser(**data_superuser)
