from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'is_verified', 'is_guest')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_filter = ('is_verified', 'is_guest', 'is_active')
    inlines = [AddressInline]
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Status', {'fields': ('is_verified', 'is_guest')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
