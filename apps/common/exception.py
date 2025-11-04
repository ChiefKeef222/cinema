from drf_standardized_errors.handler import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        try:
            error_detail = response.data["errors"][0]["detail"]
        except Exception:
            error_detail = "Ошибка сервера"

        return Response({"error": error_detail}, status=response.status_code)

    return Response({"error": "Внутренняя ошибка сервера"}, status=500)
