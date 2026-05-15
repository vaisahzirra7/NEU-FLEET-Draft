from django.urls import path
from . import views

app_name = "trips"

urlpatterns = [
    # Trips
    path("",            views.list_view,    name="list"),
    path("new/",        views.create_view,  name="create"),
    path("<int:pk>/",   views.detail_view,  name="detail"),

    # Destinations (managed list)
    path("destinations/",                  views.destination_list,   name="destination_list"),
    path("destinations/new/",              views.destination_create, name="destination_create"),
    path("destinations/<int:pk>/edit/",    views.destination_edit,   name="destination_edit"),
]
