from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    
    # Fields to display in the admin list
    list_display = ('username', 'email', 'name', 'nrp', 'role', 'department', 'shift', 'is_active', 'created_at')
    
    # Fields to filter by
    list_filter = ('role', 'department', 'shift', 'is_active', 'is_staff', 'created_at')
    
    # Fields to search
    search_fields = ('username', 'email', 'name', 'nrp', 'first_name', 'last_name')
    
    # Fields to order by
    ordering = ('-created_at',)
    
    # Fields to display in the form
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'name', 'email', 'phone')
        }),
        ('Work info', {
            'fields': ('nrp', 'role', 'department', 'shift')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # Fields for adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'name', 'phone')
        }),
        ('Work info', {
            'fields': ('nrp', 'role', 'department', 'shift')
        }),
    )
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    # Fields per page
    list_per_page = 25
    
    # Enable date hierarchy
    date_hierarchy = 'created_at'
