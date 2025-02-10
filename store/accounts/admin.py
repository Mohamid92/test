"""
Account Admin Configuration

Customizes Django admin interface for user management.
Provides tools for user administration and monitoring.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address

class AddressInline(admin.TabularInline):
    """
    Inline editor for user addresses.
    Shows:
    - Address details
    - Default status
    - Billing status
    """
    model = Address
    extra = 0

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom user admin interface.
    Features:
    - Phone number authentication
    - Verification status
    - Address management
    - Order history
    """
    list_display = [
        'phone_number', 'email', 'first_name', 'last_name',
        'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['phone_number', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    inlines = [AddressInline]
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Status'), {'fields': ('is_verified', 'is_guest')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'password1', 'password2',
                'first_name', 'last_name', 'email'
            ),
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Address management interface.
    Features:
    - Address listing
    - Default address handling
    - User association
    """
    list_display = [
        'user', 'street_address', 'city',
        'state', 'is_default', 'created_at'
    ]
    list_filter = ['is_default', 'is_billing', 'city', 'state']
    search_fields = [
        'street_address', 'city',
        'user__phone_number', 'user__email'
    ]
    raw_id_fields = ['user']
