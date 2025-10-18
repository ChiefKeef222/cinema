from apps.common.viewsets import BaseCRUDViewSet
from django_filters import rest_framework as filters
from django.db.models import Prefetch

from .serializer import HallSerializer, SessionSerializer
from .models import Session, Hall, Seat


class HallViewSet(BaseCRUDViewSet):
    # queryset = Hall.objects.all()
    serializer_class = HallSerializer

    message_create = "Зал успешно создан"
    message_update = "Зал успешно обновлён"
    message_destroy = "Зал успешно удалён"

    def get_queryset(self):
        return Hall.objects.prefetch_related(
            Prefetch(
                "seats", queryset=Seat.objects.order_by("row_number", "seat_number")
            )
        ).all()


class SessionFilter(filters.FilterSet):
    movie = filters.UUIDFilter(field_name="movie_id__public_id")
    hall = filters.UUIDFilter(field_name="hall_id__public_id")
    date = filters.DateFilter(field_name="start_time", lookup_expr="date")

    class Meta:
        model = Session
        fields = ["movie", "hall", "date"]


class SessionViewSet(BaseCRUDViewSet):
    serializer_class = SessionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SessionFilter
    message_create = "Сеанс успешно создан"
    message_update = "Сеанс успешно обновлён"
    message_destroy = "Сеанс успешно удалён"

    def get_queryset(self):
        return Session.objects.select_related("movie_id", "hall_id").all()
