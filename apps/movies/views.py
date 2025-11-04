from rest_framework import filters
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import time

from apps.common.viewsets import BaseCRUDViewSet
from .serializer import MovieSerializer
from .models import Movie


local_cache = {}
LOCAL_TTL = 60


def safe_cache_get(key):
    try:
        value = cache.get(key)
        if value:
            return value
    except Exception:
        pass

    entry = local_cache.get(key)
    if entry:
        data, expires = entry
        if time.time() < expires:
            return data
        else:
            del local_cache[key]
    return None


def safe_cache_set(key, value):
    try:
        cache.set(key, value, LOCAL_TTL)
    except Exception:
        local_cache[key] = (value, time.time() + LOCAL_TTL)


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]
    object_verbose_name = "Фильм"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_param = self.request.query_params.get("search")
        if search_param and len(search_param) > 100:
            raise ValidationError("Параметр поиска не может быть длиннее 100 символов.")
        return queryset

    # message_create = "Фильм успешно создан"
    # message_update = "Фильм успешно обновлён"
    # message_destroy = "Фильм успешно удалён"

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        cache_key = "movies_list"
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
        cache.clear()
        local_cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.clear()
        local_cache.clear()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.clear()
        local_cache.clear()
        return response
