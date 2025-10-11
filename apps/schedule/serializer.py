from rest_framework import serializers

from .models import Hall, Session
from apps.movies.models import Movie


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ["public_id", "name", "rows", "seats_per_row"]
        read_only_fields = ["public_id"]


class SessionSerializer(serializers.ModelSerializer):
    movie_id = serializers.SlugRelatedField(
        slug_field="public_id", queryset=Movie.objects.all()  # связываем по UUID фильма
    )
    hall_id = serializers.SlugRelatedField(
        slug_field="public_id", queryset=Hall.objects.all()  # связываем по UUID зала
    )

    class Meta:
        model = Session
        fields = [
            "public_id",
            "movie_id",
            "hall_id",
            "start_time",
            "price",
        ]
        read_only_fields = ["public_id"]
