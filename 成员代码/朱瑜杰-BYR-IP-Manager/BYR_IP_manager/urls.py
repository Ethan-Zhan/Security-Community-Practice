"""
URL configuration for BYR_IP_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from feishu_auth import views as feishu_auth
from bind import views as bind
from devices import views as devices
urlpatterns = [
    path("admin/", admin.site.urls),

    path("auth/feishu/redirect", feishu_auth.feishu_redirect),
    path("auth/feishu/callback", feishu_auth.callback),
    path("auth/feishu/logout", feishu_auth.feishu_logout),

    path("bind", bind.bind),
    path("verify", bind.verify),

    path("devices/<int:device_id>", devices.unbound),
    path("devices/<int:device_id>/login", devices.login),
    path("devices/<int:device_id>/logout", devices.logout),
    path("devices", devices.devices),
]
