from django.db import models
import uuid

from apps.movies.models import Movie


class Hall(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    name = models.CharField(max_length=255, unique=True, verbose_name="Название зала")

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class Seat(models.Model):
    hall = models.ForeignKey(Hall, related_name='seats', on_delete=models.CASCADE)
    row_number = models.PositiveIntegerField(verbose_name="номер ряда")
    seat_number = models.PositiveIntegerField("Номер места")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        constraints = [
            models.UniqueConstraint(
                fields=["hall", "row_number", "seat_number"],
                name="unique_hall_row_seat"
            )
        ]
        ordering = ["hall", "row_number", "seat_number"]

    def __str__(self):
        return f"Зал {self.hall.name}: ряд {self.row_number}, место {self.seat_number}"

class Session(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    movie_id = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="sessions", verbose_name="Фильм"
    )
    hall_id = models.ForeignKey(
        Hall, on_delete=models.CASCADE, related_name="sessions", verbose_name="Зал"
    )
    start_time = models.DateTimeField(verbose_name="Время начала сеанса")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Стоимость билета"
    )

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеансы"
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.movie_id.title} — {self.hall_id.name} ({self.start_time:%d.%m %H:%M})"
