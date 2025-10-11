from django.db import models
import uuid

from apps.movies.models import Movie


class Hall(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    name = models.CharField(max_length=255, unique=True, verbose_name="Название зала")
    rows = models.PositiveIntegerField(verbose_name="Количество рядов")
    seats_per_row = models.PositiveIntegerField(verbose_name="Количество мест в ряду")

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.rows} рядов × {self.seats_per_row} мест)"


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
        return f"{self.movie.title} — {self.hall.name} ({self.start_time:%d.%m %H:%M})"
