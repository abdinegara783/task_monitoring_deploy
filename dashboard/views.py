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
    RoleBasedUserCreationForm,
    LeaderQuotaForm,
)
from .models import User, ActivityReport, AnalysisReport, Notification, LeaderQuota
import csv
from django.http import HttpResponse



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
                return redirect('login')
            
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
    my_foremen = User.objects.filter(role='foreman', leader=request.user)
    total_employees = my_foremen.count()
    
    # Mendapatkan activity reports hanya dari foreman yang berada di bawah leader ini
    today = timezone.now().date()
    my_foremen_reports = ActivityReport.objects.filter(foreman__in=my_foremen)
    
    # Statistik berdasarkan reports dari foreman bawahan
    today_reports = my_foremen_reports.filter(date=today).count()
    pending_validation = my_foremen_reports.filter(status='pending').count()
    completed_reports = my_foremen_reports.filter(status__in=['approved', 'rejected']).count()
    
    # Data untuk setiap tab - PASTIKAN NAMA VARIABEL SESUAI TEMPLATE
    pending_activity_reports = my_foremen_reports.filter(status='pending').order_by('-date')
    today_activity_reports = my_foremen_reports.filter(date=today).order_by('-date')
    validated_reports = my_foremen_reports.filter(status__in=['approved', 'rejected']).order_by('-date')
    
    # Recent reports hanya dari foreman bawahan
    recent_activity_reports = my_foremen_reports.order_by('-date')[:5]
    
    stats = {
        'total_employees': total_employees,
        'today_reports': today_reports,
        'pending_validation': pending_validation,
        'completed_reports': completed_reports
    }
    
    context = {
        'stats': stats,
        'recent_activity_reports': recent_activity_reports,
        'my_foremen': my_foremen,
        'employees': my_foremen,  # Untuk tab employees-list
        'pending_activity_reports': pending_activity_reports,  # Untuk tab pending-reports
        'today_activity_reports': today_activity_reports,  # Untuk tab today-reports
        'validated_reports': validated_reports,  # Untuk tab validated-reports
    }
    
    return render(request, "leader/leader_dashboard.html", context)


@login_required
@role_required(["leader"])
def leader_validation_analysis(request):
    return render(request, "leader/leader_validation_analysis.html")


@login_required
@role_required(["leader"])
def leader_validation_activity(request):
    report_id = request.GET.get('report_id')
    
    if not report_id:
        messages.error(request, "ID laporan tidak ditemukan.")
        return redirect('leader_dashboard')
    
    try:
        report = ActivityReport.objects.get(id=report_id)
    except ActivityReport.DoesNotExist:
        messages.error(request, "Laporan tidak ditemukan.")
        return redirect('leader_dashboard')
    
    if request.method == "POST":
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        
        if action == 'approve':
            report.status = 'approved'
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan berhasil disetujui.")
            return redirect('leader_dashboard')
        elif action == 'reject':
            report.status = 'rejected'
            report.feedback = feedback
            report.save()
            messages.success(request, "Laporan berhasil ditolak.")
            return redirect('leader_dashboard')
    
    context = {
        'report': report
    }
    
    return render(request, "leader/leader_validation_activity.html", context)




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
    total_leaders = User.objects.filter(role='leader').count()
    total_foremen = User.objects.filter(role='foreman').count()
    pending_reports = ActivityReport.objects.filter(status='pending').count()
    validated_reports = ActivityReport.objects.filter(status__in=['approved', 'rejected']).count()
    
    # Data untuk tabs
    pending_activity_reports = ActivityReport.objects.filter(status='pending').order_by('-date')
    validated_activity_reports = ActivityReport.objects.filter(status__in=['approved', 'rejected']).order_by('-date')
    all_users = User.objects.all().order_by('-date_joined')
    leader_quotas = LeaderQuota.objects.all().order_by('leader_name')
    
    stats = {
        'total_users': total_users,
        'total_leaders': total_leaders,
        'total_foremen': total_foremen,
        'pending_reports': pending_reports,
        'validated_reports': validated_reports
    }
    
    context = {
        'stats': stats,
        'pending_activity_reports': pending_activity_reports,
        'validated_activity_reports': validated_activity_reports,
        'all_users': all_users,
        'leader_quotas': leader_quotas,
    }
    
    return render(request, "admin/admin_dashboard.html", context)


# Ganti decorator untuk admin_list
@login_required
@role_required(["admin"])
def admin_list(request):
    """Daftar semua karyawan untuk admin"""
    employees = User.objects.all().order_by("-created_at")

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        employees = employees.filter(
            models.Q(username__icontains=search_query)
            | models.Q(email__icontains=search_query)  # noqa: F821
            | models.Q(name__icontains=search_query)
            | models.Q(nrp__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(employees, 10)  # 10 employees per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "employees": page_obj,
        "search_query": search_query,
        "total_employees": employees.count(),
    }
    return render(request, "admin/admin_list.html", context)


# Ganti decorator untuk admin_create
@login_required
@role_required(["admin"])
def admin_create(request):
    """Form untuk admin menambah karyawan baru"""
    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(
                request, f"Karyawan {employee.username} berhasil didaftarkan!"
            )
            return redirect("admin_list")
        else:
            messages.error(request, "Terjadi kesalahan dalam pendaftaran karyawan.")
    else:
        form = EmployeeRegistrationForm()

    return render(request, "admin/admin_create.html", {"form": form})


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
            form.save()
            messages.success(
                request, f"Data karyawan {employee.username} berhasil diupdate!"
            )
            return redirect("admin_detail", user_id=employee.id)
        else:
            messages.error(request, "Terjadi kesalahan dalam update data.")
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
        return redirect("employee_list")

    return render(request, "admin/admin_delete.html", {"employee": employee})





# FOREMAN VIEW   --=-==-=--=-==------==-=-=-=-=--=---=-=-=-=-=-=-=-=-=-=-




@login_required
@role_required(["foreman"])
def Foreman_dashboard(request):
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

    notification = Notification.objects.filter(user=request.user).order_by(
        "created_at"
    )[:5]
    unread_notification = Notification.objects.filter(
        user=request.user, is_read=False
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
                    "leader": getattr(report.foreman, 'leader', None) and getattr(report.foreman.leader, 'name', None) or "-",
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
        "unread_notification": unread_notification,
    }

    return render(request, "foreman/foreman_dashboard.html", context)


@login_required
@role_required(["foreman"])
def create_activity_report(request):
    if request.method == "POST":
        form = ActivityReportForm(request.POST)
        if form.is_valid():
            activity_report = form.save(commit=False)
            activity_report.foreman = request.user
            activity_report.status = 'pending'  # Set default status
            activity_report.save()
            messages.success(request, "Laporan aktivitas berhasil dibuat!")
            return redirect("foreman_dashboard")
    else:
        form = ActivityReportForm()
    
    return render(request, "foreman/foreman_create_activity_report.html", {"form": form})


@login_required
def create_analysis_report(request):
    """Create analysis report view"""
    if request.method == "POST":
        form = AnalysisReportForm(request.POST, user=request.user)
        if form.is_valid():
            analysis_report = form.save(commit=False)
            analysis_report.foreman = request.user
            analysis_report.save()
            messages.success(request, "Analysis Report berhasil dibuat!")
            return redirect("foreman_dashboard")
        else:
            messages.error(
                request, "Terjadi kesalahan dalam pembuatan Analysis Report."
            )
    else:
        form = AnalysisReportForm(user=request.user)

    context = {"form": form, "user": request.user}

    return render(request, "foreman/create_analysis_report.html", context)


@login_required
@role_required(["foreman"])
def foreman_report_status(request):
    # Get all reports for current foreman
    activity_reports = ActivityReport.objects.filter(foreman=request.user).order_by('-date')
    analysis_reports = AnalysisReport.objects.filter(foreman=request.user).order_by('-report_date')
    
    context = {
        'activity_reports': activity_reports,
        'analysis_reports': analysis_reports,
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
            notification.is_read = True
            notification.save()
            return redirect("notifications")
        elif "mark_all_read" in request.POST:
            notifications.update(is_read=True)
            return redirect("notifications")

    # Context data
    context = {
        "notifications": notifications,
        "unread_count": notifications.filter(is_read=False).count(),
    }

    return render(request, "notification.html", context)


@login_required
def api_get_notifications(request):
    """API endpoint to get notifications for AJAX requests"""
    from django.http import JsonResponse

    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    data = {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%d %b %Y, %H:%M"),
                "notification_type": n.notification_type,
            }
            for n in notifications
        ],
    }

    return JsonResponse(data)


@login_required
@role_required(["admin", "superadmin"])
def create_user_with_role(request):
    if request.method == 'POST':
        form = RoleBasedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} berhasil dibuat dengan role {user.role}.")
            return redirect('admin_list')
    else:
        form = RoleBasedUserCreationForm()
    
    # Data untuk template
    leader_quotas = LeaderQuota.objects.filter(is_active=True)
    
    return render(request, 'admin/create_user_role_based.html', {
        'form': form,
        'leader_quotas': leader_quotas
    })

@login_required
@role_required(["admin", "superadmin"])
def manage_leader_quota(request, quota_id=None):
    if quota_id:
        quota = get_object_or_404(LeaderQuota, id=quota_id)
        form = LeaderQuotaForm(request.POST or None, instance=quota)
    else:
        form = LeaderQuotaForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Kuota leader berhasil diperbarui.")
        return redirect('leader_quota_list')
    
    return render(request, 'admin/manage_leader_quota.html', {
        'form': form,
        'quota': quota if quota_id else None
    })

@login_required
@role_required(["admin", "superadmin"])
def leader_quota_list(request):
    quotas = LeaderQuota.objects.all().order_by('leader_name')
    return render(request, 'admin/leader_quota_list.html', {
        'quotas': quotas
    })

@login_required
@role_required(["admin", "superadmin"])
def export_reports_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activity_reports.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Foreman', 'Leader', 'Unit Code', 'Component', 'Activities', 'Status', 'Feedback'])
    
    reports = ActivityReport.objects.all().order_by('-date')
    for report in reports:
        writer.writerow([
            report.date,
            report.foreman.name or report.foreman.username,
            report.foreman.leader.name if report.foreman.leader else '-',
            report.Unit_Code or '-',
            report.component or '-',
            report.activities,
            report.status,
            report.feedback or '-'
        ])
    
    return response

@login_required
@role_required(["admin", "superadmin"])
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Username', 'Email', 'Role', 'Department', 'Leader', 'NRP', 'Phone', 'Shift'])
    
    users = User.objects.all().order_by('role', 'name')
    for user in users:
        writer.writerow([
            user.name or user.username,
            user.username,
            user.email,
            user.role,
            user.department or '-',
            user.leader.name if user.leader else '-',
            user.nrp or '-',
            user.phone or '-',
            user.shift
        ])
    
    return response
