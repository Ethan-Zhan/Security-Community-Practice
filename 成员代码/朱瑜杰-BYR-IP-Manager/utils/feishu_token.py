import requests
from django.conf import settings
from django.core.cache import cache


def call_app_access_token():
    """
        飞书鉴权 需获取应用token
        如果内存中存有token则直接返回
        否则重新获取
        """
    app_access_token = cache.get(settings.APP_ACCESS_TOKEN_CACHE)
    if app_access_token:
        return app_access_token
    else:
        app_access_token = refresh_app_access_token()
        if app_access_token:
            cache.set(settings.APP_ACCESS_TOKEN_CACHE, app_access_token,
                      settings.APP_ACCESS_TOKEN_EXPIRY - 300)

        return app_access_token


def call_user_access_token(app_access_token, code):
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
    }
    response = requests.post(url, json=data, headers=headers)
    if not ("data" in response.json()):
        raise Exception("Authorization failed", response.json())
    return response.json()['data']


def refresh_app_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    data = {
        "app_id": settings.FEISHU_APP_ID,
        "app_secret": settings.FEISHU_APP_SECRET,
    }
    response = requests.post(url, json=data)
    response_data = response.json()
    app_access_token = response_data.get("app_access_token")
    return app_access_token


def get_user_info(user_access_token):
    url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
    headers = {
        "Authorization": f"Bearer {user_access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()['data']
