from rest_framework import serializers

from movies.models import Movie


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
