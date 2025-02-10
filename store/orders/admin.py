"""
Order Admin Interface

Customizes Django admin interface for order management.
Features:
- Order processing
- Payment tracking
- Refund management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, PaymentLog, Refund, StoreConfiguration
from .tasks import send_order_confirmation

class OrderItemInline(admin.TabularInline):
    """Inline editor for order items"""
    model = OrderItem
    readonly_fields = ['subtotal']
    extra = 0

class PaymentLogInline(admin.TabularInline):
    """Inline display of payment logs"""
    model = PaymentLog
    readonly_fields = ['payment_id', 'gateway', 'amount', 'status', 'created_at']
    can_delete = False
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order management interface.
    Features:
    - Status management
    - Payment tracking
    - Customer communication
    """
    list_display = [
        'order_number', 'user', 'total_amount',
        'order_status', 'payment_status', 'created_at'
    ]
    list_filter = ['order_status', 'payment_status', 'created_at']
    search_fields = [
        'order_number', 'user__email',
        'user__phone_number', 'shipping_address__street_address'
    ]
    inlines = [OrderItemInline, PaymentLogInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    actions = ['mark_as_processing', 'mark_as_shipped']

    def mark_as_processing(self, request, queryset):
        """Bulk action to mark orders as processing"""
        updated = queryset.update(order_status='PROCESSING')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"

    # ... additional admin methods ...

@admin.register(StoreConfiguration)
class StoreConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Payment Gateway Settings', {
            'fields': (
                'enable_online_payment',
                'payment_gateway',
            ),
        }),
        ('QPay Settings', {
            'classes': ('collapse',),
            'fields': ('qpay_merchant_id', 'qpay_secret_key', 'qpay_api_url'),
        }),
        ('CBQ Settings', {
            'classes': ('collapse',),
            'fields': ('cbq_merchant_id', 'cbq_secret_key', 'cbq_terminal_id'),
        }),
        ('NAPS Settings', {
            'classes': ('collapse',),
            'fields': ('naps_merchant_id', 'naps_secret_key'),
        }),
        ('QNB Settings', {
            'classes': ('collapse',),
            'fields': ('qnb_merchant_id', 'qnb_secret_key'),
        }),
        ('TAP Settings', {
            'classes': ('collapse',),
            'fields': ('tap_secret_key', 'tap_public_key'),
        }),
        ('Fatoora Settings', {
            'classes': ('collapse',),
            'fields': ('fatoora_api_key', 'fatoora_merchant_id'),
        }),
        ('Email Settings', {
            'fields': (
                'enable_order_emails',
                'smtp_host',
                'smtp_port',
                'smtp_username',
                'smtp_password',
                'from_email',
                'admin_email',
            )
        }),
    )

    def has_add_permission(self, request):
        # Only allow one configuration instance
        return not StoreConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of configuration
        return False

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_id', 'gateway', 'amount', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'created_at')
    search_fields = ('order__order_number', 'payment_id')
    readonly_fields = ('created_at', 'updated_at', 'response_data')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at', 'processed_at')
    search_fields = ('order__order_number', 'reason')
    readonly_fields = ('created_at', 'processed_at')

@admin.register(PaymentAnalytics)
class PaymentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_transactions', 'successful_transactions', 
                   'failed_transactions', 'total_amount', 'refund_amount')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_transactions', 'successful_transactions',
                      'failed_transactions', 'total_amount', 'refund_amount')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
