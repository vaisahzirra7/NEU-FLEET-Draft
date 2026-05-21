from django.urls import path
from . import views

app_name = "system_settings"

urlpatterns = [
    path("", views.edit_view, name="edit"),
]
