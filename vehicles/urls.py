from django.urls import path
from . import views

app_name = "vehicles"

urlpatterns = [
    path("",                        views.list_view,            name="list"),
    path("add/",                    views.create_view,          name="create"),
    path("fleet-licence/update/",   views.fleet_licence_update, name="fleet_licence_update"),
    path("<int:pk>/",               views.detail_view,          name="detail"),
    path("<int:pk>/edit/",          views.edit_view,            name="edit"),
    path("<int:pk>/dismiss-fuel/",  views.dismiss_fuel_reminder,name="dismiss_fuel"),
]
