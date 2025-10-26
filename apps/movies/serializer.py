from rest_framework import serializers

from .models import Movie
from apps.common.abstract import AbstractSerializer


class MovieSerializer(AbstractSerializer, serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "poster_url",
            "created_at",
            "updated_at",
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Продолжительность фильма должна быть больше 0 минут"
            )
        return value
