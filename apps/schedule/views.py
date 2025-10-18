from apps.common.viewsets import BaseCRUDViewSet

from .serializer import HallSerializer, SessionSerializer
from .models import Session, Hall


class HallViewSet(BaseCRUDViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer

    message_create = "Зал успешно создан"
    message_update = "Зал успешно обновлён"
    message_destroy = "Зал успешно удалён"


class SessionViewSet(BaseCRUDViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    message_create = "Сеанс успешно создан"
    message_update = "Сеанс успешно обновлён"
    message_destroy = "Сеанс успешно удалён"
