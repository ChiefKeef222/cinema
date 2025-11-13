from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


from apps.common.abstract import AbstractModel, AbstractManager


class UserManager(BaseUserManager, AbstractManager):
    def create_user(self, username, email, password=None, **kwargs):
        if username is None:
            raise TypeError("Пользователь должен иметь никнейм")
        if email is None:
            raise TypeError("Пользователь должен иметь имейл")
        if password is None:
            raise TypeError("Пользователь должен иметь пароль")

        email_validator = EmailValidator(
            message="Введите корректный адрес электронной почты"
        )
        email_validator(email)

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({"password": e.messages})

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

        email_validator = EmailValidator(
            message="Введите корректный адрес электронной почты"
        )
        email_validator(email)
        validate_password(password)

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.role = User.Role.ADMIN
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, AbstractModel):
    class Role(models.TextChoices):
        USER = "user", "Обычный пользователь"
        ADMIN = "admin", "Администратор"

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_user(self):
        return self.role == self.Role.USER
