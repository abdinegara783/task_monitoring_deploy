from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .forms import (
    LoginForm,
    RegisterForm,
    EmployeeRegistrationForm,
    ActivityReportForm,
    AnalysisReportForm,
    AnalysisReportExtendedForm,
    RoleBasedUserCreationForm,
    LeaderQuotaForm,
)
from .models import User, ActivityReport, AnalysisReport, Notification, LeaderQuota
import csv
from django.http import HttpResponse
from .services.pdf_service import PDFReportService
from .services.analysis_pdf_service import AnalysisPDFService
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import datetime


def hello_world_tailwind(request):
    """View untuk demo Tailwind CSS"""
    return render(request, "hello-world.html")


# ------------------------------------------------------------------------------
def is_leader(user):
    """Check if user is leader"""
    return user.is_authenticated and user.role == "leader"


def is_foreman(user):
    """Check if user is foreman"""
    return user.is_authenticated and user.role == "foreman"


# Decorator untuk redirect jika akses tidak sesuai role
def role_required(allowed_roles):
    """Decorator to check if user has the required role"""

    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.role not in allowed_roles:
                messages.error(request, "Anda tidak memiliki akses ke halaman ini.")

                # Redirect ke dashboard sesuai role
                if request.user.role == "admin":
                    return redirect("admin_dashboard")
                elif request.user.role == "leader":
                    return redirect("leader_dashboard")
                elif request.user.role == "foreman":
                    return redirect("foreman_dashboard")
                else:
                    return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


# LOGIN AND LOGOUT VIEW --=-==-=--=-==------==-=-=-=-=--=---=-=-=-=-=-=-=-=-=-=-


def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.role == "admin":
            return redirect("admin_dashboard")
        elif request.user.role == "leader":
            return redirect("leader_dashboard")  # Leader dashboard
        elif request.user.role == "foreman":
            return redirect("foreman_dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang, {user.username}!")

                # Redirect to appropriate dashboard based on role
                if user.role == "admin":
                    return redirect("admin_dashboard")
                elif user.role == "leader":
                    return redirect("leader_dashboard")  # Leader dashboard
                elif user.role == "foreman":
                    return redirect("foreman_dashboard")
                else:
                    return redirect("dashboard")  # Default dashboard
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Form tidak valid.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Anda telah berhasil logout.")
    return redirect("login")


# LEADER VIEW   --=-==-=--=-==------==-=-=-=-=--=---=-=-=-=-=-=-=-=-=-=-


@login_required
@role_required(["leader"])
def leader_dashboard(request):
    # Mendapatkan foreman yang berada di bawah leader ini
    my_foremen = User.objects.filter(role="foreman", leader=request.user)
    total_employees = my_foremen.count()

    # Mendapatkan activity reports dan analysis reports dari foreman bawahan
    today = timezone.now().date()
    my_foremen_activity_reports = ActivityReport.objects.filter(foreman__in=my_foremen)
    my_foremen_analysis_reports = AnalysisReport.objects.filter(foreman__in=my_foremen)

    # Gabungkan kedua jenis laporan dengan menambahkan field 'report_type'
    combined_reports = []

    # Tambahkan activity reports
    for report in my_foremen_activity_reports:
        combined_reports.append(
            {
                "id": report.id,
                "date": report.date,
                "foreman": report.foreman,
                "unit_code": report.Unit_Code,
                "component": report.component,
                "activities": report.activities_code,
                "status": report.status,
                "report_type": "activity",
                "report_type_display": "Activity Report",
                "validation_url": "leader_validation_activity",
                "created_at": report.created_at or report.date,
            }
        )

    # Tambahkan analysis reports
    for report in my_foremen_analysis_reports:
        combined_reports.append(
            {
                "id": report.id,
                "date": report.report_date,
                "foreman": report.foreman,
                "unit_code": report.unit_code,
                "component": report.get_problem_display() if report.problem else "-",
                "activities": report.title_problem[:50] + "..."
                if len(report.title_problem) > 50
                else report.title_problem,
                "status": report.status,
                "report_type": "analysis",
                "report_type_display": "Analysis Report",
                "validation_url": "leader_validation_analysis",
                "created_at": report.created_at or report.report_date,
            }
        )

    # Sort berdasarkan tanggal terbaru
    combined_reports.sort(key=lambda x: x["created_at"], reverse=True)

    # Filter berdasarkan status dan tanggal
    pending_reports = [r for r in combined_reports if r["status"] == "pending"]
    today_reports = [r for r in combined_reports if r["date"] == today]
    validated_reports = [
        r for r in combined_reports if r["status"] in ["approved", "rejected"]
    ]

    # Statistik
    today_reports_count = len(today_reports)
    pending_validation_count = len(pending_reports)
    completed_reports_count = len(validated_reports)

    # Recent reports (5 terbaru)
    recent_reports = combined_reports[:5]

    # Untuk semua dashboard (foreman, leader, admin)
    unread_notifications_count = Notification.objects.filter(
        user=request.user, status='unread'
    ).count()

    stats = {
        "total_employees": total_employees,
        "today_reports": today_reports_count,
        "pending_validation": pending_validation_count,
        "completed_reports": completed_reports_count,
    }

    context = {
        "stats": stats,
        "recent_reports": recent_reports,
        "my_foremen": my_foremen,
        "employees": my_foremen,  # Untuk tab employees-list
        "pending_reports": pending_reports,  # Untuk tab pending-reports
        "today_reports": today_reports,  # Untuk tab today-reports
        "validated_reports": validated_reports,  # Untuk tab validated-reports
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request, "leader/leader_dashboard.html", context)


@login_required
@role_required(["leader"])
def leader_validation_activity(request):
    report_id = request.GET.get("report_id")

    if not report_id:
        messages.error(request, "ID laporan tidak ditemukan.")
        return redirect("leader_dashboard")

    try:
        report = ActivityReport.objects.get(id=report_id, foreman__leader=request.user)
    except ActivityReport.DoesNotExist:
        messages.error(
            request, "Laporan tidak ditemukan atau Anda tidak memiliki akses."
        )
        return redirect("leader_dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        feedback = request.POST.get("feedback", "")

        if action == "approve":
            report.status = "approved"
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan aktivitas berhasil disetujui.")
            return redirect("leader_dashboard")
        elif action == "reject":
            report.status = "rejected"
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan aktivitas berhasil ditolak.")
            return redirect("leader_dashboard")

    context = {"report": report}

    return render(request, "leader/leader_validation_activity_new.html", context)


@login_required
@role_required(["leader"])
def leader_validation_analysis(request):
    report_id = request.GET.get("report_id")

    if not report_id:
        messages.error(request, "ID laporan tidak ditemukan.")
        return redirect("leader_dashboard")

    try:
        report = AnalysisReport.objects.get(id=report_id, foreman__leader=request.user)
    except AnalysisReport.DoesNotExist:
        messages.error(
            request, "Laporan tidak ditemukan atau Anda tidak memiliki akses."
        )
        return redirect("leader_dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        feedback = request.POST.get("feedback", "")

        if action == "approve":
            report.status = "approved"
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan analisis berhasil disetujui.")
            return redirect("leader_dashboard")
        elif action == "reject":
            report.status = "rejected"
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan analisis berhasil ditolak.")
            return redirect("leader_dashboard")

    context = {"report": report}

    return render(request, "leader/leader_validation_analysis_new.html", context)


# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect("dashboard")

#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success("Akun berhasil dibuat! Silakan login.")
#             return redirect("login")
#         else:
#             messages.error(request, "Terjadi kesalahan dalam pendaftaran.")
#     else:
#         form = RegisterForm()

#     return render(request, "register.html", {"form": form})


# ADMIN VIEW   --=-==-=--=-==------==-=-=-=-=--=---=-=-=-=-=-=-=-=-=-=-


# Ganti decorator untuk admin_dashboard
@login_required
@role_required(["admin", "superadmin"])
def admin_dashboard(request):
    # Statistik untuk admin
    total_users = User.objects.count()
    total_leaders = User.objects.filter(role="leader").count()
    total_foremen = User.objects.filter(role="foreman").count()
    pending_reports = ActivityReport.objects.filter(status="pending").count()
    validated_reports = ActivityReport.objects.filter(
        status__in=["approved", "rejected"]
    ).count()

    # Data untuk tabs
    pending_activity_reports = ActivityReport.objects.filter(status="pending").order_by(
        "-date"
    )
    validated_activity_reports = ActivityReport.objects.filter(
        status__in=["approved", "rejected"]
    ).order_by("-date")
    all_users = User.objects.all().order_by("-date_joined")
    leader_quotas = LeaderQuota.objects.all().order_by("leader_name")
    foremen = User.objects.filter(role="foreman", is_active=True)

    # Untuk semua dashboard (foreman, leader, admin)
    unread_notifications_count = Notification.objects.filter(
        user=request.user, status='unread'
    ).count()

    stats = {
        "total_users": total_users,
        "total_leaders": total_leaders,
        "total_foremen": total_foremen,
        "pending_reports": pending_reports,
        "validated_reports": validated_reports,
    }

    context = {
        "stats": stats,
        "pending_activity_reports": pending_activity_reports,
        "validated_activity_reports": validated_activity_reports,
        "all_users": all_users,
        "leader_quotas": leader_quotas,
        "foremen": foremen,
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request, "admin/admin_dashboard.html", context)


# Ganti decorator untuk admin_detail
@login_required
@role_required(["admin"])
def admin_detail(request, user_id):
    """Detail karyawan"""
    employee = get_object_or_404(User, id=user_id)
    return render(request, "admin/admin_detail.html", {"employee": employee})


# Ganti decorator untuk admin_edit
@login_required
@role_required(["admin"])
def admin_edit(request, user_id):
    """Edit data karyawan"""
    employee = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST, instance=employee)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, f"Data karyawan {employee.username} berhasil diupdate!"
                )
                return redirect("admin_detail", user_id=employee.id)
            except Exception as e:
                messages.error(
                    request, f"Terjadi kesalahan dalam update data: {str(e)}"
                )
        else:
            # Tampilkan error spesifik dari form
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        error_messages.append(error)
                    else:
                        field_label = form.fields[field].label or field
                        error_messages.append(f"{field_label}: {error}")

            error_text = "; ".join(error_messages)
            messages.error(
                request, f"Terjadi kesalahan dalam update data: {error_text}"
            )
    else:
        form = EmployeeRegistrationForm(instance=employee)

    return render(
        request, "admin/admin_edit.html", {"form": form, "employee": employee}
    )


# Ganti decorator untuk admin_delete
@login_required
@role_required(["admin"])
def admin_delete(request, user_id):
    """Hapus karyawan"""
    employee = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = employee.username
        employee.delete()
        messages.success(request, f"Karyawan {username} berhasil dihapus!")
        return redirect("admin_dashboard")

    return render(request, "admin/admin_delete.html", {"employee": employee})


# FOREMAN VIEW   --=-==-=--=-==------==-=-=-=-=--=---=-=-=-=-=-=-=-=-=-=-


@login_required
@role_required(["foreman"])
def foreman_dashboard(request):
    """Foreman dashboard view with combined reports in recent status"""
    # Get activity reports for current user, ordered by date (most recent first)
    activity_reports = ActivityReport.objects.filter(foreman=request.user).order_by(
        "-date", "-start_time"
    )

    # Get total reports
    total_reports = activity_reports.count()

    # Get reports from today
    today = timezone.now().date()
    today_reports = activity_reports.filter(date=today).count()

    # Get reports from this week
    week_ago = today - timedelta(days=7)
    this_week_reports = activity_reports.filter(date__gte=week_ago).count()

    # Get reports from this month
    month_start = today.replace(day=1)
    this_month_reports = activity_reports.filter(date__gte=month_start).count()

    # Check if user has submitted activity report today
    activity_report_today = activity_reports.filter(date=today).first()

    # === ANALYSIS REPORTS ===
    current_month = today.month
    current_year = today.year

    # Get all analysis reports for current user
    analysis_reports = AnalysisReport.objects.filter(foreman=request.user).order_by(
        "-report_date"
    )

    # Get analysis reports for current month
    analysis_reports_count = analysis_reports.filter(
        report_date__year=current_year, report_date__month=current_month
    ).count()

    # Analysis report requirements
    analysis_reports_required = 3  # 3 laporan per bulan
    analysis_reports_remaining = max(
        0, analysis_reports_required - analysis_reports_count
    )
    analysis_reports_complete = analysis_reports_count >= analysis_reports_required

    # Progress calculation
    analysis_progress_percentage = min(
        100, (analysis_reports_count / analysis_reports_required) * 100
    )

    # Status text
    if analysis_reports_complete:
        analysis_status_text = "Selesai bulan ini"
    else:
        analysis_status_text = f"{analysis_reports_remaining} laporan lagi"

    # === COMBINED RECENT REPORTS ===
    # Get recent activity reports (last 3)
    recent_activity_reports = activity_reports[:3]

    # Get recent analysis reports (last 2)
    recent_analysis_reports = analysis_reports[:2]

    # Combine reports for "Status Laporan Terbaru"
    combined_reports = []

    # Untuk semua dashboard (foreman, leader, admin)
    notification = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]
    unread_notifications_count = Notification.objects.filter(
        user=request.user, status='unread'
    ).count()

    # Add activity reports
    for report in recent_activity_reports:
        combined_reports.append(
            {
                "type": "activity",
                "id": report.id,
                "date": report.date,
                "title": "Activity Report",
                "description": f"{report.Unit_Code or 'N/A'} - {report.component or 'N/A'}",
                "time": f"{report.start_time} - {report.end_time}",
                "status": "completed",
                "report_data": {
                    "date": report.date.strftime("%d M Y"),
                    "start_time": str(report.start_time),
                    "end_time": str(report.end_time),
                    "unit_code": report.Unit_Code or "-",
                    "component": report.component or "-",
                    "activities": report.activities or "Tidak ada deskripsi",
                    "leader": getattr(report.foreman, "leader", None)
                    and getattr(report.foreman.leader, "name", None)
                    or "-",
                    "hmkm": report.Hmkm or "-",
                    "activities_code": report.activities_code or "-",
                },
            }
        )

    # Add analysis reports
    for report in recent_analysis_reports:
        combined_reports.append(
            {
                "type": "analysis",
                "id": report.id,
                "date": report.report_date,
                "title": "Analysis Report",
                "description": f"{report.no_report or 'N/A'} - {report.unit_code or 'N/A'}",
                "time": report.report_date.strftime("%d %b %Y"),
                "status": "completed",
                "report_data": {
                    "report_date": report.report_date.strftime("%d M Y"),
                    "no_report": report.no_report or "-",
                    "section_track": report.section_track or "-",
                    "wo_number": report.WO_Number or "-",
                    "wo_date": report.WO_date.strftime("%d M Y")
                    if report.WO_date
                    else "-",
                    "unit_code": report.unit_code or "-",
                    "problem": report.get_problem_display() if report.problem else "-",
                    "trouble_date": report.Trouble_date.strftime("%d M Y")
                    if report.Trouble_date
                    else "-",
                    "hm": report.Hm or "-",
                    "title_problem": report.title_problem or "Tidak ada deskripsi",
                    "part_no": report.part_no or "-",
                    "part_name": report.part_name or "-",
                },
            }
        )

    # Sort combined reports by date (most recent first)
    combined_reports.sort(key=lambda x: x["date"], reverse=True)
    recent_reports = combined_reports[:5]  # Take top 5 most recent

    context = {
        # Activity Report Data
        "activity_reports": activity_reports[:5],
        "recent_reports": recent_reports,  # Combined reports for template
        "total_reports": total_reports,
        "today_reports": today_reports,
        "this_week_reports": this_week_reports,
        "this_month_reports": this_month_reports,
        "activity_report_today": activity_report_today,
        # Analysis Report Data
        "analysis_reports_count": analysis_reports_count,
        "analysis_reports_required": analysis_reports_required,
        "analysis_reports_remaining": analysis_reports_remaining,
        "analysis_reports_complete": analysis_reports_complete,
        "analysis_progress_percentage": round(analysis_progress_percentage, 1),
        "analysis_status_text": analysis_status_text,
        # General Data
        "user": request.user,
        "current_time": timezone.now(),
        "month_name": today.strftime("%B %Y"),
        # Notification Data
        "notification": notification,
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request, "foreman/foreman_dashboard.html", context)


@login_required
@role_required(["foreman"])
def create_activity_report(request):
    if request.method == "POST":
        form = ActivityReportForm(request.POST)
        if form.is_valid():
            try:
                activity_report = form.save(commit=False)
                activity_report.foreman = (
                    request.user
                )  # Set foreman dari user yang login
                activity_report.status = "pending"  # Set default status
                activity_report.save()
                messages.success(
                    request,
                    "Laporan aktivitas berhasil dibuat dan menunggu validasi leader!",
                )
                return redirect("foreman_dashboard")
            except Exception as e:
                messages.error(request, f"Gagal menyimpan laporan: {str(e)}")
                print(f"Error saving activity report: {e}")  # For debugging
        else:
            # Print form errors for debugging
            print(f"Form errors: {form.errors}")
            # Show specific field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = ActivityReportForm()

    # Get user with leader relationship
    user_with_leader = User.objects.select_related("leader").get(id=request.user.id)

    context = {
        "form": form,
        "user": user_with_leader,  # Pass user with leader data
    }

    return render(request, "foreman/foreman_create_activity_report.html", context)


@login_required
@role_required(["foreman"])
def create_analysis_report(request):
    """Create analysis report view - Step 1"""
    if request.method == "POST":
        form = AnalysisReportForm(request.POST, user=request.user)
        if form.is_valid():
            analysis_report = form.save(commit=False)
            analysis_report.foreman = request.user
            analysis_report.save()
            messages.success(
                request,
                "Informasi dasar berhasil disimpan! Silakan lengkapi analisis lanjutan.",
            )
            # Redirect ke step 2
            return redirect(
                "create_analysis_report_step2", report_id=analysis_report.id
            )
        else:
            messages.error(
                request, "Terjadi kesalahan dalam pembuatan Analysis Report."
            )
    else:
        form = AnalysisReportForm(user=request.user)

    context = {"form": form, "user": request.user}

    return render(request, "foreman/foreman_create_analysis_report.html", context)


@login_required
@role_required(["foreman"])
def create_analysis_report_step2(request, report_id):
    """Step 2: Extended analysis report form"""
    try:
        # Get the existing report
        analysis_report = AnalysisReport.objects.get(id=report_id, foreman=request.user)
    except AnalysisReport.DoesNotExist:
        messages.error(
            request, "Laporan tidak ditemukan atau Anda tidak memiliki akses."
        )
        return redirect("foreman_dashboard")

    if request.method == "POST":
        form = AnalysisReportExtendedForm(
            request.POST, request.FILES, instance=analysis_report
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Analysis Report berhasil dilengkapi!")
            return redirect("foreman_dashboard")
        else:
            messages.error(
                request, "Ada kesalahan dalam form. Silakan periksa kembali."
            )
    else:
        form = AnalysisReportExtendedForm(instance=analysis_report)

    context = {"form": form, "analysis_report": analysis_report, "user": request.user}

    return render(request, "foreman/foreman_create_analysis_report_step2.html", context)


@login_required
@role_required(["foreman"])
def foreman_report_status(request):
    # Get all reports for current foreman
    activity_reports = ActivityReport.objects.filter(foreman=request.user).order_by(
        "-date"
    )
    analysis_reports = AnalysisReport.objects.filter(foreman=request.user).order_by(
        "-report_date"
    )

    context = {
        "activity_reports": activity_reports,
        "analysis_reports": analysis_reports,
    }

    return render(request, "foreman/report_status.html", context)


@login_required
@role_required(["foreman"])
def foreman_reports(request):
    """View untuk menampilkan semua laporan foreman"""
    # Get all activity reports for current user
    reports = ActivityReport.objects.filter(foreman=request.user).order_by(
        "-date", "-start_time"
    )

    # Filter berdasarkan tanggal jika ada parameter
    date_filter = request.GET.get("date")
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, "%Y-%m-%d").date()
            reports = reports.filter(date=filter_date)
        except ValueError:
            pass

    # Filter berdasarkan bulan jika ada parameter
    month_filter = request.GET.get("month")
    if month_filter:
        try:
            year, month = month_filter.split("-")
            reports = reports.filter(date__year=year, date__month=month)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(reports, 10)  # 10 reports per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_reports = reports.count()
    today = timezone.now().date()
    this_month_reports = reports.filter(
        date__year=today.year, date__month=today.month
    ).count()

    context = {
        "reports": page_obj,
        "total_reports": total_reports,
        "this_month_reports": this_month_reports,
        "user": request.user,
        "date_filter": date_filter,
        "month_filter": month_filter,
    }

    return render(request, "foreman/reports_list.html", context)


@login_required
def notifications_view(request):
    """View for displaying user notifications"""
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    # Mark notifications as read
    if request.method == "POST" and "mark_read" in request.POST:
        notification_id = request.POST.get("notification_id")
        if notification_id:
            notification = get_object_or_404(
                Notification, id=notification_id, user=request.user
            )
            notification.mark_as_read()
            return redirect("notifications")
        elif "mark_all_read" in request.POST:
            from django.utils import timezone
            notifications.filter(status='unread').update(status='read', read_at=timezone.now())
            return redirect("notifications")

    # Context data
    context = {
        "notifications": notifications,
        "unread_count": notifications.filter(status='unread').count(),
    }

    return render(request, "notification.html", context)


@login_required
def api_get_notifications(request):
    """API endpoint to get notifications for AJAX requests"""
    from django.http import JsonResponse

    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]
    unread_count = Notification.objects.filter(user=request.user, status='unread').count()

    data = {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "is_read": n.status != 'unread',
                "created_at": n.created_at.strftime("%d %b %Y, %H:%M"),
                "notification_type": n.notification_type,
            }
            for n in notifications
        ],
    }

    return JsonResponse(data)


@login_required
def api_mark_notification_read(request, notification_id):
    """API endpoint to mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(
                Notification, id=notification_id, user=request.user
            )
            notification.mark_as_read()
            
            # Return updated count
            unread_count = Notification.objects.filter(
                user=request.user, status='unread'
            ).count()
            
            return JsonResponse({
                'success': True,
                'unread_count': unread_count,
                'message': 'Notification marked as read'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@role_required(["admin", "superadmin"])
def create_user_with_role(request):
    """Create user with specific role validation"""
    
    def get_create_user_context():
        """Helper function to get context for create user template"""
        leaders = User.objects.filter(role="leader", is_active=True)
        leaders_with_quota = []
        
        for leader in leaders:
            quota = leader.quota_as_leader.first()
            if quota:
                current_count = User.objects.filter(leader=leader, role="foreman", is_active=True).count()
                available = quota.max_foreman - current_count
                leaders_with_quota.append({
                    'leader': leader,
                    'quota': quota,
                    'current_count': current_count,
                    'available': available,
                    'is_available': available > 0
                })
        
        return {
            'leaders_with_quota': leaders_with_quota,
            'departments': User.DEPARTMENT_CHOICES,
            'roles': User.ROLE_CHOICES,
            'available_leaders': User.objects.filter(role="leader", is_active=True)
        }
    
    if request.method == "POST":
        # Get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        nrp = request.POST.get("nrp")
        role = request.POST.get("role")
        department = request.POST.get("department")
        shift = request.POST.get("shift", 1)
        leader_id = request.POST.get("leader")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        
        # Basic validation
        if not all([username, email, role]):
            messages.error(request, "Username, email, dan role wajib diisi.")
            return render(request, "admin/create_user.html", get_create_user_context())
        
        # Password validation
        if password1 != password2:
            messages.error(request, "Password dan konfirmasi password tidak cocok.")
            return render(request, "admin/create_user.html", get_create_user_context())
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' sudah digunakan.")
            return render(request, "admin/create_user.html", get_create_user_context())
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' sudah digunakan.")
            return render(request, "admin/create_user.html", get_create_user_context())
        
        # Role-specific validation
        if role == "leader":
            # Validate leader quota registration
            if not LeaderQuota.is_username_registered(username):
                messages.error(
                    request,
                    f"Username '{username}' belum terdaftar di kuota leader. Silakan daftarkan terlebih dahulu."
                )
                return render(request, "admin/create_user.html", get_create_user_context())
        
        elif role == "foreman":
            # Validate leader selection
            if not leader_id:
                messages.error(request, "Mekanik harus memiliki leader.")
                return render(request, "admin/create_user.html", get_create_user_context())
            
            try:
                leader = User.objects.get(id=leader_id, role="leader")
                
                # Check leader quota menggunakan reverse relation yang baru
                quota = leader.quota_as_leader.first()
                if quota:
                    current_foremen = User.objects.filter(leader=leader, role="foreman", is_active=True).count()
                    if current_foremen >= quota.max_foreman:
                        messages.error(
                            request,
                            f"Leader {leader.name} sudah mencapai batas maksimal mekanik ({quota.max_foreman}). Saat ini: {current_foremen}/{quota.max_foreman}",
                        )
                        return render(request, "admin/create_user.html", get_create_user_context())
                else:
                    messages.error(
                        request,
                        f"Leader {leader.name} tidak memiliki kuota yang terdaftar. Silakan daftarkan kuota terlebih dahulu.",
                    )
                    return render(request, "admin/create_user.html", get_create_user_context())
            
            except User.DoesNotExist:
                messages.error(request, "Leader tidak ditemukan.")
                return render(request, "admin/create_user.html", get_create_user_context())
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                name=name,
                phone=phone,
                nrp=nrp,
                role=role,
                department=department,
                shift=int(shift),
            )
            
            # Set leader for foreman
            if role == "foreman" and leader_id:
                leader = User.objects.get(id=leader_id)
                user.leader = leader
                user.save()
                
                # Update quota count if role is foreman
                quota = leader.quota_as_leader.first()
                if quota:
                    quota.update_foreman_count()
            
            # Link leader quota for leader role
            if role == "leader":
                quota = LeaderQuota.get_quota_by_username(username)
                if quota:
                    quota.leader_user = user
                    quota.save()
            
            messages.success(
                request,
                f"User {user.name or user.username} berhasil dibuat dengan role {role}!"
            )
            return redirect("admin_dashboard")
        
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan saat membuat user: {str(e)}")
            return render(request, "admin/create_user.html", get_create_user_context())
    
    # GET request
    return render(request, "admin/create_user.html", get_create_user_context())


def get_create_user_context():
    """Helper function to get context for create user form"""
    # Get available leaders for foreman assignment
    available_leaders = User.objects.filter(role="leader", is_active=True)

    return {
        "available_leaders": available_leaders,
    }


@login_required
@role_required(["admin", "superadmin"])
def manage_leader_quota(request, quota_id=None):
    if quota_id:
        quota = get_object_or_404(LeaderQuota, id=quota_id)
        form = LeaderQuotaForm(request.POST or None, instance=quota)
    else:
        form = LeaderQuotaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kuota leader berhasil diperbarui.")
        return redirect("admin_dashboard")

    return render(
        request,
        "admin/manage_leader_quota.html",
        {"form": form, "quota": quota if quota_id else None},
    )


@login_required
@role_required(["admin", "superadmin"])
def leader_quota_list(request):
    quotas = LeaderQuota.objects.all().order_by("leader_name")
    return render(request, "admin/leader_quota_list.html", {"quotas": quotas})


@login_required
@role_required(["admin", "superadmin"])
def export_reports_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="activity_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Date",
            "Foreman",
            "Leader",
            "Unit Code",
            "Component",
            "Activities",
            "Status",
            "Feedback",
        ]
    )

    reports = ActivityReport.objects.all().order_by("-date")
    for report in reports:
        writer.writerow(
            [
                report.date,
                report.foreman.name or report.foreman.username,
                report.foreman.leader.name if report.foreman.leader else "-",
                report.Unit_Code or "-",
                report.component or "-",
                report.activities,
                report.status,
                report.feedback or "-",
            ]
        )

    return response


@login_required
@role_required(["admin", "superadmin"])
def export_users_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Name",
            "Username",
            "Email",
            "Role",
            "Department",
            "Leader",
            "NRP",
            "Phone",
            "Shift",
        ]
    )

    users = User.objects.all().order_by("role", "name")
    for user in users:
        writer.writerow(
            [
                user.name or user.username,
                user.username,
                user.email,
                user.role,
                user.department or "-",
                user.leader.name if user.leader else "-",
                user.nrp or "-",
                user.phone or "-",
                user.shift,
            ]
        )

    return response


@login_required
@role_required(["admin", "superadmin"])
def export_activity_reports_pdf(request):
    """Export Activity Reports to PDF"""
    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    status = request.GET.get("status")
    foreman_id = request.GET.get("foreman")

    # Build query
    reports = ActivityReport.objects.select_related("foreman").all()

    # Apply filters
    if start_date:
        reports = reports.filter(date__gte=start_date)
    if end_date:
        reports = reports.filter(date__lte=end_date)
    if status:
        reports = reports.filter(status=status)
    if foreman_id:
        reports = reports.filter(foreman_id=foreman_id)

    # Order by date
    reports = reports.order_by("-date")

    # Generate date range string
    date_range = None
    if start_date and end_date:
        date_range = f"{start_date} s/d {end_date}"
    elif start_date:
        date_range = f"Mulai {start_date}"
    elif end_date:
        date_range = f"Sampai {end_date}"

    # Generate PDF
    pdf_service = PDFReportService()
    return pdf_service.generate_activity_reports_pdf(reports, date_range)


@login_required
@role_required(["admin", "superadmin"])
def export_analysis_reports_pdf(request):
    """Export Analysis Reports to PDF using new TAR format"""
    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    status = request.GET.get("status")
    foreman_id = request.GET.get("foreman")

    # Build query
    reports = AnalysisReport.objects.select_related("foreman", "foreman__leader").all()

    # Apply filters
    if start_date:
        reports = reports.filter(report_date__gte=start_date)
    if end_date:
        reports = reports.filter(report_date__lte=end_date)
    if status:
        reports = reports.filter(status=status)
    if foreman_id:
        reports = reports.filter(foreman_id=foreman_id)

    # Order by date
    reports = reports.order_by("-report_date")

    # Check if we have reports
    if not reports.exists():
        messages.warning(
            request,
            "Tidak ada laporan analisis yang ditemukan dengan filter yang dipilih.",
        )
        return redirect("admin_dashboard")

    try:
        # For multiple reports, we'll create a combined PDF or individual PDFs
        # Let's create individual PDFs for each report in a ZIP file
        import zipfile
        import io
        from django.http import HttpResponse

        if reports.count() == 1:
            # Single report - generate single TAR PDF
            pdf_service = AnalysisPDFService()
            return pdf_service.generate_technical_analysis_report_pdf(reports.first())
        else:
            # Multiple reports - create ZIP with individual TAR PDFs
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                pdf_service = AnalysisPDFService()

                for i, report in enumerate(reports, 1):
                    # Generate PDF for each report
                    pdf_response = pdf_service.generate_technical_analysis_report_pdf(
                        report
                    )
                    pdf_content = pdf_response.content

                    # Create filename
                    filename = f"TAR_{report.no_report or report.id}_{report.report_date.strftime('%Y%m%d')}.pdf"

                    # Add to ZIP
                    zip_file.writestr(filename, pdf_content)

            # Prepare response
            zip_buffer.seek(0)
            response = HttpResponse(
                zip_buffer.getvalue(), content_type="application/zip"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="Technical_Analysis_Reports_{datetime.now().strftime("%Y%m%d")}.zip"'
            )

            return response

    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect("admin_dashboard")


@login_required
@role_required(["admin", "superadmin"])
def pdf_export_page(request):
    """PDF Export page with filters"""
    # Get available foremen for filter
    foremen = User.objects.filter(role="foreman", is_active=True)

    context = {
        "foremen": foremen,
    }

    return render(request, "admin/pdf_export.html", context)


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
def notification_monitor(request):
    """Halaman monitoring dan pengiriman notifikasi manual"""
    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get all foremen
    foremen = User.objects.filter(role='foreman', is_active=True).order_by('name')
    
    foremen_status = []
    activity_complete_count = 0
    activity_pending_count = 0
    analysis_pending_count = 0
    
    for foreman in foremen:
        # Check activity report today
        has_activity_today = ActivityReport.objects.filter(
            foreman=foreman,
            date=today
        ).exists()
        
        # Check analysis reports this month
        analysis_count = AnalysisReport.objects.filter(
            foreman=foreman,
            report_date__month=current_month,
            report_date__year=current_year
        ).count()
        
        analysis_remaining = max(0, 3 - analysis_count)
        
        foremen_status.append({
            'id': foreman.id,
            'name': foreman.name,
            'username': foreman.username,
            'shift': foreman.shift,
            'has_activity_today': has_activity_today,
            'analysis_count': analysis_count,
            'analysis_remaining': analysis_remaining,
        })
        
        # Count for summary
        if has_activity_today:
            activity_complete_count += 1
        else:
            activity_pending_count += 1
            
        if analysis_count < 3:
            analysis_pending_count += 1
    
    context = {
        'foremen_status': foremen_status,
        'today': today,
        'total_foremen': len(foremen),
        'activity_complete_count': activity_complete_count,
        'activity_pending_count': activity_pending_count,
        'analysis_pending_count': analysis_pending_count,
    }
    
    return render(request, 'admin/notification_monitor.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
@require_http_methods(["POST"])
def send_activity_reminder(request, user_id):
    """Kirim reminder activity report ke user tertentu (Manual)"""
    try:
        user = User.objects.get(id=user_id, role='foreman', is_active=True)
        
        # Check if already has report today
        today = timezone.now().date()
        has_report = ActivityReport.objects.filter(
            foreman=user,
            date=today
        ).exists()
        
        if has_report:
            return JsonResponse({
                'success': False,
                'message': f'{user.name} sudah mengisi activity report hari ini'
            })
        
        # Create manual reminder notification
        deadline_text = "18:00" if user.shift == 1 else "05:00"
        shift_text = "Shift 1" if user.shift == 1 else "Shift 2"
        
        notification = Notification.objects.create(
            user=user,
            title=f"📧 Reminder Manual - Activity Report ({shift_text})",
            message=f"Reminder manual dari admin {request.user.name}: Harap segera isi activity report hari ini. Deadline: {deadline_text}. Silakan login ke sistem untuk mengisi laporan.",
            notification_type='activity_reminder',
            priority='high',
            created_by=request.user,
            is_manual=True,
            requires_acknowledgment=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Reminder activity berhasil dikirim ke {user.name}',
            'notification_id': notification.id
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
@require_http_methods(["POST"])
def send_analysis_reminder(request, user_id):
    """Kirim reminder analysis report ke user tertentu (Manual)"""
    try:
        user = User.objects.get(id=user_id, role='foreman', is_active=True)
        
        # Check analysis reports this month
        current_month = timezone.now().month
        current_year = timezone.now().year
        analysis_count = AnalysisReport.objects.filter(
            foreman=user,
            report_date__month=current_month,
            report_date__year=current_year
        ).count()
        
        missing_count = max(0, 3 - analysis_count)
        
        if missing_count == 0:
            return JsonResponse({
                'success': False,
                'message': f'{user.name} sudah lengkap analysis report bulan ini'
            })
        
        # Create manual reminder notification
        notification = Notification.objects.create(
            user=user,
            title=f"📊 Reminder Manual - Analysis Report",
            message=f"Reminder manual dari admin {request.user.name}: Anda masih kekurangan {missing_count} analysis report bulan ini. Harap segera dilengkapi. Silakan login ke sistem untuk mengisi laporan.",
            notification_type='analysis_reminder',
            priority='high',
            created_by=request.user,
            is_manual=True,
            requires_acknowledgment=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Reminder analysis berhasil dikirim ke {user.name} (kurang {missing_count} laporan)',
            'notification_id': notification.id
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
@require_http_methods(["POST"])
def send_bulk_activity_reminder(request):
    """Kirim reminder activity report ke semua foremen yang belum mengisi"""
    try:
        today = timezone.now().date()
        
        # Get foremen who haven't submitted activity report today
        foremen_without_report = User.objects.filter(
            role='foreman',
            is_active=True
        ).exclude(
            id__in=ActivityReport.objects.filter(
                date=today
            ).values_list('foreman_id', flat=True)
        )
        
        sent_count = 0
        for foreman in foremen_without_report:
            deadline_text = "18:00" if foreman.shift == 1 else "05:00"
            shift_text = "Shift 1" if foreman.shift == 1 else "Shift 2"
            
            Notification.objects.create(
                user=foreman,
                title=f"📧 Reminder Bulk - Activity Report ({shift_text})",
                message=f"Reminder dari admin: Harap segera isi activity report hari ini. Deadline: {deadline_text}",
                notification_type='activity_reminder'
            )
            sent_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Reminder activity berhasil dikirim ke {sent_count} foremen'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
@require_http_methods(["POST"])
def send_bulk_analysis_reminder(request):
    """Kirim reminder analysis report ke semua foremen yang kurang laporan"""
    try:
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        foremen = User.objects.filter(role='foreman', is_active=True)
        sent_count = 0
        
        for foreman in foremen:
            analysis_count = AnalysisReport.objects.filter(
                foreman=foreman,
                report_date__month=current_month,
                report_date__year=current_year
            ).count()
            
            missing_count = max(0, 3 - analysis_count)
            
            if missing_count > 0:
                Notification.objects.create(
                    user=foreman,
                    title=f"📊 Reminder Bulk - Analysis Report",
                    message=f"Reminder dari admin: Anda masih kekurangan {missing_count} analysis report bulan ini. Harap segera dilengkapi.",
                    notification_type='analysis_reminder'
                )
                sent_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Reminder analysis berhasil dikirim ke {sent_count} foremen'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })

@login_required
@role_required(["admin", "superadmin"])
def api_check_leader_quota(request):
    """API untuk cek apakah username terdaftar di leader quota"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({
                'is_registered': False,
                'message': 'Username tidak boleh kosong'
            })
        
        # Cek di LeaderQuota
        is_registered = LeaderQuota.is_username_registered(username)
        quota_info = None
        
        if is_registered:
            quota = LeaderQuota.get_quota_by_username(username)
            if quota:
                quota_info = {
                    'leader_name': quota.leader_name,
                    'max_foreman': quota.max_foreman,
                    'current_count': quota.current_foreman_count,
                    'available_slots': quota.available_slots
                }
        
        return JsonResponse({
            'is_registered': is_registered,
            'quota_info': quota_info,
            'message': 'Username terdaftar' if is_registered else 'Username belum terdaftar'
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@role_required(["admin", "leader"])
def export_single_analysis_report_pdf(request, report_id):
    """Export single analysis report as PDF"""
    try:
        report = AnalysisReport.objects.select_related(
            "foreman", "foreman__leader"
        ).get(id=report_id)

        pdf_service = AnalysisPDFService()
        return pdf_service.generate_technical_analysis_report_pdf(report)

    except AnalysisReport.DoesNotExist:
        messages.error(request, "Analysis report tidak ditemukan.")
        return redirect("admin_dashboard")
    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect("admin_dashboard")


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
def send_custom_notification(request):
    """Kirim notifikasi custom ke user tertentu atau grup"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            title = data.get('title', '').strip()
            message = data.get('message', '').strip()
            priority = data.get('priority', 'medium')
            user_ids = data.get('user_ids', [])
            requires_ack = data.get('requires_acknowledgment', False)
            
            if not title or not message:
                return JsonResponse({
                    'success': False,
                    'message': 'Title dan message wajib diisi'
                })
            
            if not user_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'Pilih minimal satu user'
                })
            
            # Create notifications for selected users
            notifications_created = []
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id, is_active=True)
                    notification = Notification.objects.create(
                        user=user,
                        title=f"📢 {title}",
                        message=f"Pesan dari admin {request.user.name}: {message}",
                        notification_type='manual_message',
                        priority=priority,
                        created_by=request.user,
                        is_manual=True,
                        requires_acknowledgment=requires_ack
                    )
                    notifications_created.append(notification.id)
                except User.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Notifikasi berhasil dikirim ke {len(notifications_created)} user',
                'notification_ids': notifications_created
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Format data tidak valid'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            })
    
    # GET request - show form
    users = User.objects.filter(role='foreman', is_active=True).order_by('name')
    return render(request, 'admin/send_custom_notification.html', {
        'users': users
    })


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'superadmin'])
def notification_analytics(request):
    """Analytics untuk notifikasi yang dikirim admin"""
    # Get notification statistics
    total_sent = Notification.objects.filter(is_manual=True).count()
    unread_count = Notification.objects.filter(is_manual=True, status='unread').count()
    acknowledged_count = Notification.objects.filter(is_manual=True, status='acknowledged').count()
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        is_manual=True
    ).select_related('user', 'created_by').order_by('-created_at')[:20]
    
    # Notification by type
    type_stats = Notification.objects.filter(is_manual=True).values(
        'notification_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    context = {
        'total_sent': total_sent,
        'unread_count': unread_count,
        'acknowledged_count': acknowledged_count,
        'recent_notifications': recent_notifications,
        'type_stats': type_stats,
    }
    
    return render(request, 'admin/notification_analytics.html', context)
