from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Auth
    path("login/",        views.login_view,        name="login"),
    path("logout/",       views.logout_view,        name="logout"),

    # Users
    path("users/",        views.users_list,         name="users"),
    path("users/create/", views.user_create,        name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit,   name="user_edit"),

    # Roles
    path("roles/",        views.roles_list,         name="roles"),
    path("roles/create/", views.role_create,        name="role_create"),
    path("roles/<int:pk>/edit/", views.role_edit,   name="role_edit"),

    # Departments
    path("departments/",              views.departments_list,   name="departments"),
    path("departments/create/",       views.department_create,  name="department_create"),
    path("departments/<int:pk>/edit/",views.department_edit,    name="department_edit"),
]
