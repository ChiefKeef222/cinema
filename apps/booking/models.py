from django.db import models
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

from apps.common.abstract import AbstractModel
from apps.users.models import User
from apps.schedule.models import Session, Seat


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Ожидает оплаты"
    CONFIRMED = "confirmed", "Оплачено"
    CANCELLED = "cancelled", "Отменено"
    EXPIRED = "expired", "Истекло время оплаты"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Ожидание"
    PAID = "paid", "Оплачено"
    FAILED = "failed", "Ошибка оплаты"


class Booking(AbstractModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="bookings", verbose_name="Сеанс"
    )
    seats = models.ManyToManyField(Seat, related_name="bookings", verbose_name="Места")
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="Статус",
    )
    total_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Сумма бронирования",
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Время истечения брони"
    )

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]

    def clean(self):
        invalid_seats = self.seats.exclude(hall=self.session.hall)
        if invalid_seats.exists():
            raise ValidationError("Некоторые места не принадлежат залу этого сеанса.")

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)

        if not self.total_amount:
            seat_count = self.seats.count() if self.pk else 0
            self.total_amount = (
                self.session.price * seat_count if seat_count else self.session.price
            )

        super().save(*args, **kwargs)

    def __str__(self):
        seats_list = ", ".join(
            [f"ряд {s.row_number}, место {s.seat_number}" for s in self.seats.all()]
        )
        return f"{self.user} | {self.session} | {seats_list or '—'}"


class Payment(AbstractModel):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Бронирование",
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Сумма оплаты"
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Статус оплаты",
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
        ordering = ["-created_at"]

    def clean(self):
        if self.booking.status in [BookingStatus.CANCELLED, BookingStatus.EXPIRED]:
            raise ValidationError("Нельзя оплатить отменённую или истекшую бронь.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def mark_as_paid(self):
        self.status = PaymentStatus.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

        self.booking.status = BookingStatus.CONFIRMED
        self.booking.save(update_fields=["status"])

    def mark_as_failed(self):
        self.status = PaymentStatus.FAILED
        self.save(update_fields=["status"])

        self.booking.status = BookingStatus.CANCELLED
        self.booking.save(update_fields=["status"])

    def __str__(self):
        return f"Оплата #{self.id} | {self.booking.user} | {self.get_status_display()}"
