from django.urls import path
from . import views

urlpatterns = [
    path("hello/", views.hello_world, name="hello_world"),
    path("hello-template/", views.hello_template, name="hello_template"),
    path("hello-world/", views.hello_world_tailwind, name="hello_world_tailwind"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    # Admin URLs for Employee Management
    path("administrasi/", views.employee_list, name="employee_list"),
    path("administrasi/create/", views.employee_create, name="employee_create"),
    path("administrasi/<int:user_id>/", views.employee_detail, name="employee_detail"),
    path("administrasi/<int:user_id>/edit/", views.employee_edit, name="employee_edit"),
    path(
        "administrasi/<int:user_id>/delete/",
        views.employee_delete,
        name="employee_delete",
    ),
    # Foreman URLs
    path("foreman/", views.Foreman_view, name="foreman"),
    path(
        "foreman/create_activity_report/",
        views.create_activity_report,
        name="create_activity_report",
    ),
    path(
        "foreman/create_analysis_report/",
        views.create_analysis_report,
        name="create_analysis_report",
    ),
]
