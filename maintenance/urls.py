from django.urls import path
from . import views

app_name = "maintenance"

urlpatterns = [
    path("",               views.list_view,   name="list"),
    path("add/",           views.create_view, name="create"),
    path("<int:pk>/",      views.detail_view, name="detail"),
]
