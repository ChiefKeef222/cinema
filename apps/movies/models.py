from django.db import models
import uuid


class Movie(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    title = models.CharField(
        max_length=255, verbose_name="Название фильма", db_index=True
    )
    description = models.TextField(max_length=1000, verbose_name="Описание фильма")
    duration = models.IntegerField(verbose_name="Продолжительность в минутах")
    poster_url = models.URLField(verbose_name="ссылка на постер")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title
