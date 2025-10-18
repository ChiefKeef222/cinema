from rest_framework import serializers

from .models import Hall, Session, Seat
from apps.movies.models import Movie


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["row_number", "seat_number"]


class HallSerializer(serializers.ModelSerializer):
    rows = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        ),
        write_only=True
    )

    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Hall
        fields = ('public_id', 'name', 'rows', 'seats')
        read_only_fields = ["seats"]

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        hall = Hall.objects.create(**validated_data)

        for row_data in rows_data:
            row_number = row_data.get('row_number')
            seats_count = row_data.get('seats')
            for seat_num in range(1, seats_count + 1):
                Seat.objects.create(hall=hall, row_number=row_number, seat_number=seat_num)

        return hall


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
