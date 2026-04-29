from django.urls import path
from . import views

app_name = "fuel_logs"

urlpatterns = [
    path("",        views.list_view,   name="list"),
    path("redeem/", views.create_view, name="create"),
]
