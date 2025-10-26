from django.db import models
import uuid

from apps.common.abstract import AbstractModel

class Movie(AbstractModel, models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(
        max_length=255, verbose_name="Название фильма", db_index=True
    )
    description = models.TextField(max_length=1000, verbose_name="Описание фильма")
    duration = models.IntegerField(verbose_name="Продолжительность в минутах")
    poster_url = models.URLField(verbose_name="ссылка на постер")

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title
