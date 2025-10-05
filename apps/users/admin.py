from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin interface"""
    
    list_display = [
        'username', 
        'email', 
        'get_full_name', 
        'premium_badge',
        'email_verified_badge',
        'is_staff', 
        'created_at'
    ]
    
    list_filter = [
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'is_premium',
        'is_email_verified',
        'created_at'
    ]
    
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'last_login_ip']
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 
                'last_name', 
                'date_of_birth', 
                'bio',
                'phone_number',
                'profile_picture'
            )
        }),
        ('Preferences', {
            'fields': ('currency', 'timezone'),
            'classes': ('collapse',)
        }),
        ('Premium Status', {
            'fields': ('is_premium', 'premium_expires_at'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser',
                'is_email_verified',
                'groups', 
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2',
                'first_name',
                'last_name',
                'is_staff',
                'is_active'
            )
        }),
    )
    
    def premium_badge(self, obj):
        """Display premium status with colored badge"""
        if obj.is_premium_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px; font-weight: bold;">⭐ Premium</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 10px; border-radius: 3px;">Free</span>'
        )
    premium_badge.short_description = 'Plan'
    
    def email_verified_badge(self, obj):
        """Display email verification status"""
        if obj.is_email_verified:
            return format_html(
                '<span style="color: #28a745;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Not Verified</span>'
        )
    email_verified_badge.short_description = 'Email Status'
    
    def get_full_name(self, obj):
        """Display full name"""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'