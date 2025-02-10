"""
Order Signal Handlers

Handles model signals for orders and payments.
Updates related data and triggers notifications.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, PaymentLog, Refund
from .tasks import process_order, process_successful_payment

@receiver(post_save, sender=Order)
def handle_order_creation(sender, instance, created, **kwargs):
    """Handle new order creation"""
    if created:
        process_order.delay(instance.id)

@receiver(pre_save, sender=Order)
def store_original_status(sender, instance, **kwargs):
    """Stores original status for comparison"""
    if instance.id:
        try:
            instance._original_status = Order.objects.get(id=instance.id).order_status
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=PaymentLog)
def handle_payment_status_change(sender, instance, created, **kwargs):
    """Handle payment status updates"""
    if instance.status == 'SUCCESS':
        process_successful_payment.delay(instance.id)

@receiver(post_save, sender=Refund)
def handle_refund_status_change(sender, instance, created, **kwargs):
    """
    Handles refund status changes.
    Triggers:
    - Customer notifications
    - Payment reversals
    - Analytics updates
    """
    if instance.status == 'APPROVED':
        PaymentNotificationManager.send_refund_approval(instance)
        
        # Process refund through payment gateway
        from .tasks import process_refund
        process_refund.delay(instance.id)
