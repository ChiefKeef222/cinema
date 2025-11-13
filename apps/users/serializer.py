from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from .models import User
from apps.common.abstract import AbstractSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator


class UserSerializer(AbstractSerializer, serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True, required=True
    )
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken.for_user(self.user)

        refresh["role"] = self.user.role
        refresh["username"] = self.user.username

        data["user"] = UserSerializer(self.user).data
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
