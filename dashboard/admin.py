from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityReport, AnalysisReport


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""

    # Fields to display in the admin list
    list_display = (
        "username",
        "email",
        "name",
        "nrp",
        "role",
        "department",
        "shift",
        "leader",
        "is_active",
        "created_at",
    )

    # Fields to filter by
    list_filter = ("role", "department", "shift", "is_active", "is_staff", "created_at")

    # Fields to search
    search_fields = ("username", "email", "name", "nrp", "first_name", "last_name")

    # Fields to order by
    ordering = ("-created_at",)

    # Fields to display in the form
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "name", "email", "phone")},
        ),
        ("Work info", {"fields": ("nrp", "role", "department", "shift")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    # Fields for adding new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
        ("Personal info", {"fields": ("first_name", "last_name", "name", "phone")}),
        ("Work info", {"fields": ("nrp", "role", "department", "shift")}),
    )

    # Read-only fields
    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")

    # Fields per page
    list_per_page = 25

    # Enable date hierarchy
    date_hierarchy = "created_at"
    # Enable search
    search_fields = ("username", "email", "name", "nrp", "first_name", "last_name")
    # Enable list filter
    list_filter = ("role", "department", "shift", "is_active", "is_staff", "created_at")


@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    """Admin configuration for ActivityReport"""

    list_display = (
        "id",
        "foreman",
        "date",
        "shift",
        "component",
        "activities_code",
        "Unit_Code",
        "start_time",
        "end_time",
        "feedback",
        "created_at",
        "status",
    )

    # Remove "leader" from list_filter
    list_filter = (
        "foreman",
        "date",
        "shift",
        "component",
        "activities_code",
        # "leader"  # Remove this line
    )

    # Corrected search_fields
    search_fields = (
        "foreman__username",
        "foreman__name",
        "Unit_Code",
        "activities",
        "component",
    )

    # Ordering by date (most recent first)
    ordering = ("-date", "-start_time")

    # Date hierarchy for easy navigation
    date_hierarchy = "date"

    # Fields per page
    list_per_page = 25

    # Fieldsets for organized form display
    fieldsets = (
        ("Basic Information", {"fields": ("foreman", "date", "shift")}),
        ("Time Information", {"fields": ("start_time", "end_time")}),
        (
            "Work Details",
            {
                # Remove "leader" from this fieldset
                "fields": ("Unit_Code", "Hmkm", "component", "activities_code")
            },
        ),
        ("Activities", {"fields": ("activities", "feedback"), "classes": ("wide",)}),
        ("Status", {"fields": ("status",), "classes": ("wide",)}),
    )

    # Read-only fields (if any)
    readonly_fields = ()

    # Custom methods for better display
    def get_foreman_name(self, obj):
        return obj.foreman.name or obj.foreman.get_full_name()

    get_foreman_name.short_description = "Foreman Name"
    get_foreman_name.admin_order_field = "foreman__name"

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            from datetime import datetime

            start = datetime.combine(obj.date, obj.start_time)
            end = datetime.combine(obj.date, obj.end_time)
            duration = end - start
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f} jam"
        return "-"

    get_duration.short_description = "Duration"

    # Add custom methods to list_display if needed
    # list_display = list_display + ("get_foreman_name", "get_duration")


# Tambahkan atau update di admin.py

@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = [
        'foreman', 'report_date', 'unit_code', 'problem', 
        'status', 'created_at'
    ]
    list_filter = [
        'status', 'problem', 'section_track', 'report_date',
        'faktor_man', 'faktor_material', 'faktor_machine', 
        'faktor_method', 'faktor_environment'
    ]
    search_fields = [
        'foreman__name', 'foreman__username', 'unit_code', 
        'title_problem', 'part_no', 'part_name'
    ]
    readonly_fields = ['created_at']
    
    fieldsets = [
        ('Informasi Dasar', {
            'fields': (
                'foreman', 'section_track', 'email', 'no_report',
                'report_date', 'WO_Number', 'WO_date'
            )
        }),
        ('Detail Masalah', {
            'fields': (
                'unit_code', 'problem', 'Trouble_date', 'Hm',
                'title_problem', 'part_no', 'part_name'
            )
        }),
        ('Analisis Masalah', {
            'fields': (
                'nama_fungsi_komponen', 'gejala_masalah', 
                'akar_penyebab_masalah'
            )
        }),
        ('Faktor 4M1E', {
            'fields': (
                'faktor_man', 'faktor_material', 'faktor_machine',
                'faktor_method', 'faktor_environment'
            ),
            'classes': ['collapse']
        }),
        ('Tindakan', {
            'fields': (
                'tindakan_dilakukan', 'tindakan_pencegahan'
            )
        }),
        ('Dokumentasi', {
            'fields': (
                'dokumentasi_sebelum', 'dokumentasi_sesudah'
            )
        }),
        ('Status & Feedback', {
            'fields': (
                'status', 'feedback', 'created_at'
            )
        })
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('foreman')

    def get_foreman_name(self, obj):
        return obj.foreman.name or obj.foreman.get_full_name()

    get_foreman_name.short_description = "Foreman Name"
    get_foreman_name.admin_order_field = "foreman__name"

    def get_problem_display_name(self, obj):
        return obj.get_problem_display() if obj.problem else "-"

    get_problem_display_name.short_description = "Problem Type"
    get_problem_display_name.admin_order_field = "problem"

    def get_section_display_name(self, obj):
        return obj.get_section_track_display() if obj.section_track else "-"

    get_section_display_name.short_description = "Section"
    get_section_display_name.admin_order_field = "section_track"
