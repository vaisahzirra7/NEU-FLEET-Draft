from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("",             views.reports_index,      name="index"),
    path("vehicles/",    views.vehicle_spending,   name="vehicle_spending"),
    path("monthly/",     views.monthly_expense,    name="monthly_expense"),
    path("maintenance/", views.maintenance_report, name="maintenance_report"),
]
