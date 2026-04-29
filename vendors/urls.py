from django.urls import path
from . import views

app_name = "vendors"

urlpatterns = [
    path("",               views.list_view,   name="list"),
    path("add/",           views.create_view, name="create"),
    path("<int:pk>/edit/", views.edit_view,   name="edit"),
]
