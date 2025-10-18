from apps.common.viewsets import BaseCRUDViewSet

from .serializer import MovieSerializer
from .models import Movie
from rest_framework import filters


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


    message_create = "Фильм успешно создан"
    message_update = "Фильм успешно обновлён"
    message_destroy = "Фильм успешно удалён"
