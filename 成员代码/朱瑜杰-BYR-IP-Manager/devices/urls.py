# bind/urls.py
from django.urls import path
from .views import unbound, login, logout, devices

app_name = "bind"

urlpatterns = [
    path("devices/<int:device_id>/", unbound, name="unbound"),
    path("devices/<int:device_id>/login", login, name="login"),
    path("devices/<int:device_id>/logout", logout, name="logout"),
    path("devices", devices, name="devices"),
    # other paths...
]