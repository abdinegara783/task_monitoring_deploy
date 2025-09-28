from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityReport, AnalysisReport, Notification, ActivityReportDetail


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


class ActivityReportDetailInline(admin.TabularInline):
    model = ActivityReportDetail
    extra = 1
    max_num = 5
    fields = ('activity_number', 'unit_code', 'hm_km', 'start_time', 'stop_time', 'component', 'activities', 'activity_code')
    ordering = ('activity_number',)


@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    """Admin configuration for new ActivityReport structure"""
    
    list_display = (
        "id",
        "foreman",
        "nrp",
        "section",
        "date",
        "get_activities_count",
        "status",
        "created_at",
    )

    list_filter = (
        "foreman",
        "section",
        "date",
        "status",
        "created_at",
    )

    search_fields = (
        "foreman__username",
        "foreman__name",
        "nrp",
        "section",
    )

    ordering = ("-date", "-created_at")

    date_hierarchy = "date"

    list_per_page = 25

    fieldsets = (
        ("Basic Information", {"fields": ("foreman", "nrp", "section", "date")}),
        ("Status", {"fields": ("status", "feedback"), "classes": ("wide",)}),
    )

    readonly_fields = ("created_at",)
    
    inlines = [ActivityReportDetailInline]

    def get_foreman_name(self, obj):
        return obj.foreman.name or obj.foreman.get_full_name()

    get_foreman_name.short_description = "Foreman Name"
    get_foreman_name.admin_order_field = "foreman__name"

    def get_activities_count(self, obj):
        return obj.activities.count()

    get_activities_count.short_description = "Activities Count"


@admin.register(ActivityReportDetail)
class ActivityReportDetailAdmin(admin.ModelAdmin):
    """Admin configuration for ActivityReportDetail"""
    
    list_display = (
        "activity_report",
        "activity_number",
        "unit_code",
        "hm_km",
        "start_time",
        "stop_time",
        "component",
        "activity_code",
    )

    list_filter = (
        "activity_report__date",
        "component",
        "activity_code",
        "activity_report__foreman",
    )

    search_fields = (
        "activity_report__foreman__username",
        "activity_report__foreman__name",
        "unit_code",
        "activities",
    )

    ordering = ("activity_report__date", "activity_number")

    fieldsets = (
        ("Report Information", {"fields": ("activity_report", "activity_number")}),
        ("Unit Information", {"fields": ("unit_code", "hm_km")}),
        ("Time Information", {"fields": ("start_time", "stop_time")}),
        ("Work Details", {"fields": ("component", "activity_code")}),
        ("Activities", {"fields": ("activities",), "classes": ("wide",)}),
    )


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

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'status', 'created_at', 'created_by']
    list_filter = ['status', 'created_at', 'created_by']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__name']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Notifikasi', {
            'fields': ('title', 'message', 'recipient')
        }),
        ('Status & Waktu', {
            'fields': ('status', 'created_at', 'read_at')
        }),
        ('Pengirim', {
            'fields': ('created_by',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'created_by')
    
    def get_recipient_name(self, obj):
        return obj.recipient.name or obj.recipient.username
    get_recipient_name.short_description = "Penerima"
    get_recipient_name.admin_order_field = "recipient__name"
