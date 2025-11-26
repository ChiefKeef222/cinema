from rest_framework import filters
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
import time

from apps.common.viewsets import BaseCRUDViewSet
from .serializer import MovieSerializer
from .models import Movie


local_cache = {}
LOCAL_TTL = 60


def safe_cache_get(key):
    value = cache.get(key)
    if value is not None:
        return value

    entry = local_cache.get(key)
    if entry:
        data, expires = entry
        if time.time() < expires:
            return data
        local_cache.pop(key, None)
    return None


def safe_cache_set(key, value):
    cache.set(key, value, LOCAL_TTL)
    local_cache[key] = (value, time.time() + LOCAL_TTL)


def clear_movies_cache():
    for key in list(local_cache.keys()):
        if key.startswith("movies_list_"):
            del local_cache[key]
    try:
        cache.delete_pattern("movies_list_*")
    except Exception:
        pass


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    filterset_fields = {"start_time": ["date"]}
    search_fields = ["title"]
    object_verbose_name = "Фильм"

    def filter_queryset(self, queryset):
        search_param = self.request.query_params.get("search")
        if search_param and len(search_param) > 100:
            raise ValidationError("Параметр поиска не может быть длиннее 100 символов.")
        return super().filter_queryset(queryset)

    def list(self, request, *args, **kwargs):
        search_param = request.query_params.get("search", "").strip().lower()
        cache_key = f"movies_list_{search_param or 'all'}"

        cached_data = safe_cache_get(cache_key)
        if cached_data:
            return self.get_response(cached_data)

        response = super().list(request, *args, **kwargs)
        safe_cache_set(cache_key, response.data)
        return response

    def get_response(self, data):
        from rest_framework.response import Response

        return Response(data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        clear_movies_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        clear_movies_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        clear_movies_cache()
        return response
