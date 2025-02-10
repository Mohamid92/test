from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.PROTECT)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        from datetime import datetime
        return f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.objects.count() + 1:04d}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

class StoreConfiguration(models.Model):
    PAYMENT_GATEWAY_CHOICES = [
        ('CASH', 'Cash Only'),
        ('QPAY', 'QPay'),
        ('CBQ', 'CBQ Payment Gateway'),
        ('NAPS', 'NAPS Gateway'),
        ('QNB', 'QNB Pay'),
        ('TAP', 'Tap Payments'),
        ('FATOORA', 'Fatoora'),
        ('OOREDOO', 'Ooredoo Money'),
    ]

    # Payment Settings
    enable_online_payment = models.BooleanField(default=False)
    payment_gateway = models.CharField(
        max_length=20,
        choices=PAYMENT_GATEWAY_CHOICES,
        default='CASH'
    )
    
    # Qatar Payment Gateway Credentials
    qpay_merchant_id = models.CharField(max_length=255, blank=True)
    qpay_secret_key = models.CharField(max_length=255, blank=True)
    qpay_api_url = models.URLField(blank=True)
    
    cbq_merchant_id = models.CharField(max_length=255, blank=True)
    cbq_secret_key = models.CharField(max_length=255, blank=True)
    cbq_terminal_id = models.CharField(max_length=255, blank=True)
    
    naps_merchant_id = models.CharField(max_length=255, blank=True)
    naps_secret_key = models.CharField(max_length=255, blank=True)
    
    qnb_merchant_id = models.CharField(max_length=255, blank=True)
    qnb_secret_key = models.CharField(max_length=255, blank=True)
    
    ooredoo_merchant_id = models.CharField(max_length=255, blank=True)
    ooredoo_api_key = models.CharField(max_length=255, blank=True)

    # Additional Payment Gateway Settings
    tap_secret_key = models.CharField(max_length=255, blank=True)
    tap_public_key = models.CharField(max_length=255, blank=True)
    
    fatoora_api_key = models.CharField(max_length=255, blank=True)
    fatoora_merchant_id = models.CharField(max_length=255, blank=True)

    # Notification Settings
    enable_sms_notifications = models.BooleanField(default=False)
    sms_provider = models.CharField(
        max_length=20,
        choices=[('OOREDOO', 'Ooredoo'), ('VODAFONE', 'Vodafone')],
        blank=True
    )
    sms_api_key = models.CharField(max_length=255, blank=True)

    # Email Settings
    enable_order_emails = models.BooleanField(default=False)
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    from_email = models.EmailField(blank=True)
    admin_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Store Configuration'
        verbose_name_plural = 'Store Configuration'

    def __str__(self):
        return 'Store Configuration'

    def save(self, *args, **kwargs):
        if not self.pk and StoreConfiguration.objects.exists():
            # Only allow one configuration instance
            return
        super().save(*args, **kwargs)

class PaymentLog(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('INITIATED', 'Payment Initiated'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_logs')
    payment_id = models.CharField(max_length=255)
    gateway = models.CharField(max_length=20, choices=StoreConfiguration.PAYMENT_GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    response_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PROCESSED', 'Processed'),
        ('REJECTED', 'Rejected')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='PENDING')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

class PaymentAnalytics(models.Model):
    date = models.DateField(unique=True)
    total_transactions = models.IntegerField(default=0)
    successful_transactions = models.IntegerField(default=0)
    failed_transactions = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = 'Payment Analytics'
