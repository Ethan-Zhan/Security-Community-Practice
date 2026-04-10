import datetime
import string
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from bind.models import BindInfo
from utils.exception.exception import (
    InvalidException,
    OutdatedException,
    UnauthorizedException,
)


def token_generate(user: User) -> string:
    payload = {
        "username": user.username,
        "exp": (timezone.now() + datetime.timedelta(hours=6)).timestamp(),
    }
    token = jwt.encode(payload, settings.JWT_KEY, algorithm="HS256")
    return token


def token_pass(header: dict) -> string:
    if "token" not in header:
        raise UnauthorizedException()
    token = header["token"]
    key = settings.JWT_KEY
    try:
        info = jwt.decode(token, key, algorithms=["HS256"])
    except Exception:
        raise InvalidException()

    if not ("exp" in info and "username" in info):
        raise InvalidException()

    if info["exp"] < timezone.now().timestamp():
        raise OutdatedException()

    return token


def bind_token_generate(bind: BindInfo) -> string:
    payload = {
        "open_id": bind.user.open_id,
        "ip": bind.ip,
        "exp": (timezone.now() + datetime.timedelta(days=3)).timestamp(),
    }
    token = jwt.encode(payload, settings.JWT_KEY, algorithm="HS256")
    return token


def bind_token_pass(header: dict) -> string:
    if "token" not in header:
        raise UnauthorizedException()
    token = header["token"]
    key = settings.JWT_KEY
    try:
        info = jwt.decode(token, key, algorithms=["HS256"])
    except Exception:
        raise InvalidException()

    if not ("exp" in info and "open_id" in info and "ip" in info):
        raise InvalidException()

    if info["exp"] < timezone.now().timestamp():
        raise OutdatedException()

    if info["exp"] - timezone.now().timestamp() <= 86400:
        new_token = bind_token_generate(BindInfo.objects.get(user__open_id=info["openid"], ip=info["ip"]))
        return new_token

    return token


def bind_get_user_info(token: string) -> dict:
    bind_token_pass({"token": token})
    key = settings.JWT_KEY
    try:
        info = jwt.decode(token, key, algorithms=["HS256"])
    except Exception:
        raise InvalidException()
    return info


