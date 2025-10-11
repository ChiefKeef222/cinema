# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
#
# from users.permissions import IsAdmin
#
# from .serializer import HallSerializer, SessionSerializer
# from .models import Session, Hall
#
#
# class HallViewSet(viewsets.ModelViewSet):
#     queryset = Hall.objects.all()
#     serializer_class = HallSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     lookup_field = "public_id"
#
#     def get_permissions(self):
#         if self.action in ["create", "update", "partial_update", "destroy"]:
#             self.permission_classes = [IsAdmin]
#         else:
#             self.permission_classes = [IsAuthenticatedOrReadOnly]
#         return super().get_permissions()
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(
#             {
#                 "message": "Зал успешно создан",
#                 "id": str(serializer.instance.public_id),
#             },
#             status=status.HTTP_201_CREATED,
#         )
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop("partial", False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(
#             {
#                 "message": "Информация о зале обновлена",
#                 "id": str(serializer.instance.public_id),
#             }
#         )
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response({"message": "Зал успешно удалён"})
#
#
# class SessionViewSet(viewsets.ModelViewSet):
#     queryset = Session.objects.all()
#     serializer_class = SessionSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     lookup_field = "public_id"
#
#     def get_permissions(self):
#         if self.action in ["create", "update", "partial_update", "destroy"]:
#             self.permission_classes = [IsAdmin]
#         else:
#             self.permission_classes = [IsAuthenticatedOrReadOnly]
#         return super().get_permissions()
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(
#             {
#                 "message": "Сеанс успешно создан",
#                 "id": str(serializer.instance.public_id),
#             },
#             status=status.HTTP_201_CREATED,
#         )
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop("partial", False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(
#             {
#                 "message": "Информация о сеансе обновлена",
#                 "id": str(serializer.instance.public_id),
#             }
#         )
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response({"message": "Сеанс успешно удалён"})
from common.views import BaseCRUDViewSet

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
