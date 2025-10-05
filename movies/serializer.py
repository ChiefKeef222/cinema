from rest_framework import serializers

from movies.models import User, Movie


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "public_id",
            "title",
            "description",
            "duration",
            "poster_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["public_id", "created_at", "updated_at"]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Продолжительность фильма должна быть больше 0 минут"
            )
        return value
