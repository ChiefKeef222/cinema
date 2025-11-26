from rest_framework import serializers

from apps.booking.models import Booking, Payment, BookingStatus, PaymentStatus
from apps.schedule.models import Seat, Session


class BookingCreateSerializer(serializers.Serializer):
    session = serializers.UUIDField()
    seats = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        ),
    )

    def validate(self, attrs):
        from apps.schedule.models import Seat
        from apps.booking.models import Booking

        try:
            session = Session.objects.get(public_id=attrs["session"])
        except Session.DoesNotExist:
            raise serializers.ValidationError("Сеанс не найден.")

        seat_coords = attrs["seats"]
        hall = session.hall

        seats = []
        for coord in seat_coords:
            try:
                seat = Seat.objects.get(
                    hall=hall,
                    row_number=coord["row_number"],
                    seat_number=coord["seat_number"],
                )
                seats.append(seat)
            except Seat.DoesNotExist:
                raise serializers.ValidationError(
                    f"Место ряд={coord['row_number']}, место={coord['seat_number']} не существует в этом зале."
                )

        already_booked = Booking.objects.filter(
            session=session,
            seats__in=seats,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        ).distinct()

        if already_booked.exists():
            taken = []
            for b in already_booked:
                for s in b.seats.all():
                    taken.append(
                        {"row_number": s.row_number, "seat_number": s.seat_number}
                    )
            raise serializers.ValidationError(
                {"error": "Некоторые места уже заняты", "taken": taken}
            )

        attrs["session_obj"] = session
        attrs["seats_obj"] = seats
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        session = validated_data["session_obj"]
        seats = validated_data["seats_obj"]

        booking = Booking.objects.create(
            user=user,
            session=session,
        )
        booking.seats.add(*seats)
        booking.save()
        return booking


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["row_number", "seat_number"]


class BookingListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    seats = SeatSerializer(many=True)
    session_title = serializers.CharField(source="session.movie.title", read_only=True)
    session_start = serializers.DateTimeField(
        source="session.start_time", read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "session_title",
            "session_start",
            "status",
            "total_amount",
            "expires_at",
            "seats",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "amount", "status", "paid_at"]
        read_only_fields = ["amount", "status", "paid_at"]

    def create(self, validated_data):
        booking = validated_data["booking"]

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            status=PaymentStatus.PENDING,
        )

        return payment
