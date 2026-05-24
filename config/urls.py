from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from reports.views import dashboard

urlpatterns = [
    path("admin/",       admin.site.urls),
    path("auth/",        include("accounts.urls")),
    path("dashboard/",   dashboard, name="dashboard"),
    path("vehicles/",    include("vehicles.urls")),
    path("generators/",  include("generators.urls")),
    path("drivers/",     include("drivers.urls")),
    path("vendors/",     include("vendors.urls")),
    path("coupons/",     include("coupons.urls")),
    path("fuel-logs/",   include("fuel_logs.urls")),
    path("maintenance/", include("maintenance.urls")),
    path("reports/",     include("reports.urls")),
    path("audit/",       include("audit.urls")),
    path("trips/",       include("trips.urls")),
    path("settings/",    include("system_settings.urls")),
    path("deposits/",    include("station_deposits.urls")),
    path("",             lambda req: redirect("dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
