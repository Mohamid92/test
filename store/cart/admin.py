"""
Cart Admin Configuration

Customizes Django admin interface for cart management.
Provides:
- Cart and cart item management
- Filtering and search capabilities
- Read-only fields for calculated values
"""

from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    """
    Inline editor for cart items.
    Shows:
    - Product details
    - Quantity
    - Subtotal
    """
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal']
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for carts.
    Features:
    - Cart item management
    - User/session filtering
    - Total calculation
    """
    list_display = ['id', 'user', 'session_id', 'item_count', 'total', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'session_id']
    readonly_fields = ['total', 'item_count']
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        """Display number of items in cart"""
        return obj.items.count()
    
    def total(self, obj):
        """Display cart total"""
        return obj.total
