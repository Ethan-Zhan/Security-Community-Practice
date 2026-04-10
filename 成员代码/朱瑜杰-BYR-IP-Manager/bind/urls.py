# bind/urls.py
from django.urls import path
from .views import bind, verify

app_name = "bind"

urlpatterns = [
    path("bind/", bind, name="bind"),
    path("verify/", verify, name="verify"),
    # other paths...
]