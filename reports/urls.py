from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("",                  views.reports_index,      name="index"),
    path("vehicles/",         views.vehicle_spending,   name="vehicle_spending"),
    path("generators/",       views.generator_spending, name="generator_spending"),
    path("monthly/",          views.monthly_expense,    name="monthly_expense"),
    path("maintenance/",      views.maintenance_report, name="maintenance_report"),
    path("driver-payments/",  views.driver_payments,    name="driver_payments"),

    # Report scheduling
    path("schedules/",                    views.schedule_list,     name="schedule_list"),
    path("schedules/create/",             views.schedule_create,   name="schedule_create"),
    path("schedules/<int:pk>/edit/",      views.schedule_edit,     name="schedule_edit"),
    path("schedules/<int:pk>/delete/",    views.schedule_delete,   name="schedule_delete"),
    path("schedules/<int:pk>/send-now/",  views.schedule_send_now, name="schedule_send_now"),
]
