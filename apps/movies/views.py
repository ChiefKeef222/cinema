from apps.common.viewsets import BaseCRUDViewSet

from .serializer import MovieSerializer
from .models import Movie
from rest_framework import filters
from rest_framework.exceptions import ValidationError


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_param = self.request.query_params.get("search")
        if search_param and len(search_param) > 100:
            raise ValidationError("Параметр поиска не может быть длиннее 100 символов.")
        return queryset

    message_create = "Фильм успешно создан"
    message_update = "Фильм успешно обновлён"
    message_destroy = "Фильм успешно удалён"
