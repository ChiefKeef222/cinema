from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404


class UserManager(BaseUserManager):
    def get_object_by_public_id(self, public_id):
        try:
            instance = self.get(public_id=public_id)
            return instance
        except (ObjectDoesNotExist, ValueError, TypeError):
            raise Http404("Пользователь не найден")

    def create_user(self, username, email, password=None, **kwargs):
        if username is None:
            raise TypeError("Пользователь должен иметь никнейм")
        if email is None:
            raise TypeError("Пользователь должен иметь имейл")
        if password is None:
            raise TypeError("Пользователь должен иметь пароль")

        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password, **kwargs):
        if password is None:
            raise TypeError("Суперпользователь должен иметь пароль")
        if email is None:
            raise TypeError("Суперпользователь должен иметь имейл")
        if username is None:
            raise TypeError("Суперпользователь должен иметь никнейм")

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=10, choices=[("user", "User"), ("admin", "Admin")], default="user"
    )
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

