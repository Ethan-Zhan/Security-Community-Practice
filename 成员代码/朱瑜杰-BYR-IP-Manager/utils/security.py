import json
import logging

from django.conf import settings
from django.http import JsonResponse


logger = logging.getLogger(__name__)


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return body if isinstance(body, dict) else None


def error_response(message, status=400):
    return JsonResponse({"status": "failed", "message": message}, status=status)


def server_error_response(exc, context):
    logger.exception("%s failed: %s", context, exc)
    debug_message = str(exc) if settings.DEBUG else "Server error"
    return error_response(debug_message, status=500)


def current_user(request):
    user = request.user
    if not user or not user.is_authenticated:
        return None
    return user


def get_request_ip(request):
    trusted_proxies = getattr(settings, "TRUSTED_PROXY_IPS", [])
    remote_addr = request.META.get("REMOTE_ADDR")
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for and remote_addr in trusted_proxies:
        return forwarded_for.split(",")[0].strip()
    return remote_addr
