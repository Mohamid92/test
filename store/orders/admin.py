from django.contrib import admin
from .models import Order, OrderItem, StoreConfiguration, PaymentLog, Refund, PaymentAnalytics

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'phone_number', 'total_amount', 'order_status', 'payment_status', 'created_at')
    list_filter = ('order_status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'phone_number', 'user__phone_number')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

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
