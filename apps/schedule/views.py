from rest_framework import status
from rest_framework.response import Response
from uuid import UUID
from datetime import datetime

from apps.common.viewsets import BaseCRUDViewSet
from django_filters import rest_framework as filters
from django.db.models import Prefetch

from .serializer import HallSerializer, SessionSerializer
from .models import Session, Hall, Seat


class HallViewSet(BaseCRUDViewSet):
    serializer_class = HallSerializer
    object_verbose_name = "Сеанс"

    # message_create = "Зал успешно создан"
    # message_update = "Зал успешно обновлён"
    # message_destroy = "Зал успешно удалён"

    def get_queryset(self):
        return Hall.objects.prefetch_related(
            Prefetch(
                "seats", queryset=Seat.objects.order_by("row_number", "seat_number")
            )
        ).all()


class SessionFilter(filters.FilterSet):
    movie_id = filters.UUIDFilter(field_name="movie_id__public_id")
    hall_id = filters.UUIDFilter(field_name="hall_id__public_id")
    date = filters.DateFilter(field_name="start_time", lookup_expr="date")

    class Meta:
        model = Session
        fields = ["movie_id", "hall_id", "date"]


class SessionViewSet(BaseCRUDViewSet):
    serializer_class = SessionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SessionFilter
    object_verbose_name = "Сеанс"

    # message_create = "Сеанс успешно создан"
    # message_update = "Сеанс успешно обновлён"
    # message_destroy = "Сеанс успешно удалён"

    def get_queryset(self):
        return Session.objects.select_related("movie_id", "hall_id").all()

    def list(self, request, *args, **kwargs):
        movie_id = request.query_params.get("movie_id")
        hall_id = request.query_params.get("hall_id")
        date_str = request.query_params.get("date")

        for name, value in request.query_params.items():
            if len(value) > 100:
                return Response(
                    {"detail": f"Параметр '{name}' превышает 100 символов."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        def is_valid_uuid(value):
            try:
                UUID(str(value))
                return True
            except (ValueError, TypeError):
                return False

        if movie_id and not is_valid_uuid(movie_id):
            return Response(
                {"detail": "Параметр 'movie_id' должен быть UUID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hall_id and not is_valid_uuid(hall_id):
            return Response(
                {"detail": "Параметр 'hall_id' должен быть UUID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {
                        "detail": "Неверный формат даты. Используйте ISO 8601 (YYYY-MM-DD)."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        response = super().list(request, *args, **kwargs)

        if not response.data:
            return Response([], status=status.HTTP_200_OK)

        return response
