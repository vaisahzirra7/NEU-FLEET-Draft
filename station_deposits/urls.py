from django.urls import path
from . import views

app_name = "station_deposits"

urlpatterns = [
    path("",            views.list_view,   name="list"),
    path("create/",     views.create_view, name="create"),
    path("<int:pk>/delete/", views.delete_view, name="delete"),
]
