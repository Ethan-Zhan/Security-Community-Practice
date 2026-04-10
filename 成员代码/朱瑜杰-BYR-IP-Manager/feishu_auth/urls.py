# feishu_auth/urls.py
from django.urls import path
from .views import feishu_redirect, callback, feishu_logout

app_name = "users"

urlpatterns = [
    path("auth/feishu/redirect/", feishu_redirect, name="feishu_redirect"),
    path("auth/feishu/callback/", callback, name="callback"),
    path("auth/feishu/logout/", feishu_logout, name="feishu_logout"),
    # other paths...
]