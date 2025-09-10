from django.urls import path
from . import views

# Tambahkan URL untuk API
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
    # Tambahkan ke urlpatterns
    path('export/reports/', views.export_reports_csv, name='export_reports_csv'),
    path('export/users/', views.export_users_csv, name='export_users_csv'),
    # Tambahkan ke urlpatterns
    path('foreman/report-status/', views.foreman_report_status, name='foreman_report_status'),
    # Tambahkan atau update URL patterns
    path('superadmin/create-user/', views.create_user_with_role, name='create_user_with_role'),
    path('superadmin/quota/manage/', views.manage_leader_quota, name='manage_leader_quota'),
    path('auperadmin/quota/manage/<int:quota_id>/', views.manage_leader_quota, name='manage_leader_quota'),
    # Tambahkan URL patterns untuk PDF export
    path('superadmin/pdf-export/', views.pdf_export_page, name='pdf_export_page'),
    path('superadmin/export/activity-reports-pdf/', views.export_activity_reports_pdf, name='export_activity_reports_pdf'),
    path('superadmin/export/analysis-reports-pdf/', views.export_analysis_reports_pdf, name='export_analysis_reports_pdf'),
    # Tambahkan URL baru setelah URL create_analysis_report yang ada
    path('foreman/create-analysis-report/step2/<int:report_id>/', views.create_analysis_report_step2, name='create_analysis_report_step2'),
    # Tambahkan URL untuk download single analysis report
    path('superadmin/export/analysis-report/<int:report_id>/pdf/', views.export_single_analysis_report_pdf, name='export_single_analysis_report_pdf'),
    path('api/check-leader-quota/', views.api_check_leader_quota, name='api_check_leader_quota'),
]
