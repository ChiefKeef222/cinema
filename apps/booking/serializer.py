from rest_framework import serializers

class SeatCoordSerializer(serializers.Serializer):
    row_number = serializers.IntegerField()
    seat_number = serializers.IntegerField()

class BookingCreateSerializer(serializers.Serializer):
    session = serializers.UUIDField()
    seats = serializers.ListField(
        child=SeatCoordSerializer(),
        min_length=1
    )
