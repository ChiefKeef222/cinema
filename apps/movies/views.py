from apps.common.views import BaseCRUDViewSet

from .serializer import MovieSerializer
from .models import Movie


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    message_create = "Фильм успешно создан"
    message_update = "Фильм успешно обновлён"
    message_destroy = "Фильм успешно удалён"
