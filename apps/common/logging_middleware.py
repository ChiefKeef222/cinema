import logging
import time
from datetime import datetime

logger = logging.getLogger("cinema")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "log_level": "INFO",
            "log_message": "Request processed",
            "http_method": request.method,
            "http_path": request.path,
            "http_status": response.status_code,
            "duration_sec": round(duration, 4),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "ip_address": self.get_client_ip(request),
        }

        if response.status_code >= 400:
            log_data["log_level"] = "ERROR"
            log_data["log_message"] = "Request failed"

        logger.info("", extra=log_data)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
