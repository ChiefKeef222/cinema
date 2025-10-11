from django.contrib import admin
from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "duration", "created_at", "updated_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
