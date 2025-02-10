"""
Order Utility Functions

Provides helper functions for order processing and validation.
Used by:
- Order views
- Payment processing
- Webhook handlers
"""

from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Order, PaymentLog, PaymentAnalytics

def generate_order_number():
    """
    Generates unique order number with format: ORD-YYYYMMDD-XXXX
    Used by:
    - Order creation
    - Order model save method
    """
    timestamp = timezone.now().strftime('%Y%m%d')
    last_order = Order.objects.filter(
        order_number__startswith=f'ORD-{timestamp}'
    ).order_by('order_number').last()
    
    if last_order:
        last_number = int(last_order.order_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f'ORD-{timestamp}-{new_number:04d}'

def validate_payment_signature(payment_data, signature, gateway):
    """
    Validates payment gateway webhook signatures.
    Used by:
    - Payment webhooks
    - Payment verification
    """
    from .payment_gateways.factory import PaymentGatewayFactory
    gateway_handler = PaymentGatewayFactory.get_gateway(gateway)
    return gateway_handler.verify_signature(payment_data, signature)

def update_payment_analytics(payment_log):
    """
    Updates payment analytics after successful/failed payments.
    Used by:
    - Payment webhooks
    - Payment verification
    """
    date = payment_log.created_at.date()
    analytics, created = PaymentAnalytics.objects.get_or_create(date=date)
    
    analytics.total_transactions += 1
    if payment_log.status == 'SUCCESS':
        analytics.successful_transactions += 1
        analytics.total_amount += payment_log.amount
    elif payment_log.status == 'FAILED':
        analytics.failed_transactions += 1
    
    analytics.save()

def calculate_order_totals(cart_items):
    """
    Calculates order totals from cart items.
    Used by:
    - Order creation
    - Cart checkout
    """
    total = Decimal('0.00')
    for item in cart_items:
        price = item.product.sale_price or item.product.price
        total += price * item.quantity
    return total
