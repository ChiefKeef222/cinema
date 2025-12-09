from rest_framework import serializers

from .models import Hall, Session, Seat
from apps.movies.models import Movie
from apps.common.abstract import AbstractSerializer


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["row_number", "seat_number"]
        ref_name = "ScheduleSeat"


class HallSerializer(AbstractSerializer, serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    rows = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        ),
        write_only=True,
    )

    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Hall
        fields = ("id", "name", "rows", "seats")
        read_only_fields = ["public_id", "seats"]

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        hall = Hall.objects.create(**validated_data)

        for row_data in rows_data:
            row_number = row_data.get("row_number")
            seats_count = row_data.get("seats")
            for seat_num in range(1, seats_count + 1):
                Seat.objects.create(
                    hall=hall, row_number=row_number, seat_number=seat_num
                )

        return hall

    def validate_rows(self, value):
        # 1) Проверяем пустой список
        if not value:
            raise serializers.ValidationError("Rows list cannot be empty.")

        # 2) Проверяем seats для каждой строки
        for row in value:
            seats = row.get("seats")
            if seats is None:
                raise serializers.ValidationError("Seats count is required.")
            if seats <= 0:
                raise serializers.ValidationError(
                    "Seats count must be greater than zero."
                )
        return value

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows", None)

        # обновляем простые поля (name и т.п.)
        instance = super().update(instance, validated_data)

        if rows_data is not None:
            # удаляем старые места
            instance.seats.all().delete()

            # создаём новые
            for row_data in rows_data:
                row_number = row_data.get("row_number")
                seats_count = row_data.get("seats")
                for seat_num in range(1, seats_count + 1):
                    Seat.objects.create(
                        hall=instance, row_number=row_number, seat_number=seat_num
                    )

        return instance


class SessionSerializer(AbstractSerializer, serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    movie = serializers.SlugRelatedField(
        slug_field="public_id", queryset=Movie.objects.all()
    )
    hall = serializers.SlugRelatedField(
        slug_field="public_id", queryset=Hall.objects.all()
    )

    class Meta:
        model = Session
        fields = [
            "id",
            "movie",
            "hall",
            "start_time",
            "price",
        ]
        read_only_fields = ["public_id"]
