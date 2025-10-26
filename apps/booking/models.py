from django.db import models

from apps.common.abstract import AbstractModel
from apps.users.models import User
from apps.schedule.models import Session, Seat


class Booking(AbstractModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="booked_seats"
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="booked_seats"
    )
    seats = models.ManyToManyField(Seat, related_name="booked_seats")

    class Meta:
        verbose_name = "Бронированное место"
        verbose_name_plural = "Бронированные места"

    def __str__(self):
        return f"{self.seats} | {self.session}"
