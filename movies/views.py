from common.views import BaseCRUDViewSet

from movies.serializer import MovieSerializer
from movies.models import Movie


class MovieViewSet(BaseCRUDViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    message_create = "Фильм успешно создан"
    message_update = "Фильм успешно обновлён"
    message_destroy = "Фильм успешно удалён"