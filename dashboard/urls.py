from django.urls import path
from . import views

urlpatterns = [
    path("hello-world/", views.hello_world_tailwind, name="hello_world_tailwind"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("register/", views.register_view, name="register"),
    # Admin URLs for Employee Management
    path("superadmin/", views.admin_dashboard, name="admin_dashboard"),
    path("superadmin/list", views.admin_list, name="admin_list"),
    path("superadmin/create/", views.admin_create, name="admin_create"),
    path("superadmin/<int:user_id>/", views.admin_detail, name="admin_detail"),
    path("superadmin/<int:user_id>/edit/", views.admin_edit, name="admin_edit"),
    path(
        "superadmin/<int:user_id>/delete/",
        views.admin_delete,
        name="admin_delete",
    ),
    # Foreman URLs
    path("foreman/", views.Foreman_dashboard, name="foreman_dashboard"),
    path("foreman/reports/", views.foreman_reports, name="foreman_reports"),
    # Activity report
    path(
        "activity-report/create/",
        views.create_activity_report,
        name="create_activity_report",
    ),
    # Analysis report
    path(
        "analysis-report/create/",
        views.create_analysis_report,
        name="create_analysis_report",
    ),
    # Leader URLs
    path("leader/", views.leader_dashboard, name="leader_dashboard"),
    path(
        "leader/analysis/",
        views.leader_validation_analysis,
        name="leader_validation_analysis",
    ),
    path(
        "leader/activity/",
        views.leader_validation_activity,
        name="leader_validation_activity",
    ),
    
    # Notification URLs
    path("notifications/", views.notifications_view, name="notifications"),
    path("api/notifications/", views.api_get_notifications, name="api_notifications"),
]
