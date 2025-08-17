from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityReport


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


@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    """Custom Activity Report Admin"""

    # Corrected list_display - using actual fields from ActivityReport model
    list_display = (
        "id", 
        "foreman", 
        "date", 
        "shift", 
        "component", 
        "activities_code",
        "Unit_Code",
        "start_time",
        "end_time"
    )
    
    # Corrected list_filter - using actual fields
    list_filter = (
        "foreman", 
        "date", 
        "shift", 
        "component", 
        "activities_code",
        "leader"
    )
    
    # Corrected search_fields
    search_fields = (
        "foreman__username", 
        "foreman__name", 
        "Unit_Code", 
        "activities",
        "component"
    )
    
    # Ordering by date (most recent first)
    ordering = ("-date", "-start_time")
    
    # Date hierarchy for easy navigation
    date_hierarchy = "date"
    
    # Fields per page
    list_per_page = 25
    
    # Fieldsets for organized form display
    fieldsets = (
        ("Basic Information", {
            "fields": ("foreman", "date", "shift")
        }),
        ("Time Information", {
            "fields": ("start_time", "end_time")
        }),
        ("Work Details", {
            "fields": ("leader", "Unit_Code", "Hmkm", "component", "activities_code")
        }),
        ("Activities", {
            "fields": ("activities",),
            "classes": ("wide",)
        }),
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
            from datetime import datetime, timedelta
            start = datetime.combine(obj.date, obj.start_time)
            end = datetime.combine(obj.date, obj.end_time)
            duration = end - start
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f} jam"
        return "-"
    get_duration.short_description = "Duration"
    
    # Add custom methods to list_display if needed
    # list_display = list_display + ("get_foreman_name", "get_duration")
