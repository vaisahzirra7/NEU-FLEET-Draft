from django.urls import path
from . import views

app_name = "coupons"

urlpatterns = [
    path("",                  views.list_view,       name="list"),
    path("issue/",            views.create_view,     name="create"),
    path("issue/bulk/",       views.bulk_issue_view, name="bulk_issue"),
    path("<int:pk>/",         views.detail_view,     name="detail"),
    path("<int:pk>/print/",   views.print_slip,      name="print_slip"),
    path("lookup/",           views.lookup_ajax,     name="lookup"),
]
