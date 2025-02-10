from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import signals
from .models import Order, OrderItem
from .notifications import NotificationManager

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    notifications = NotificationManager()
    
    if created:
        notifications.send_notification(instance, 'order_confirmation')
    else:
        if instance.tracker.has_changed('order_status'):
            if instance.order_status == 'SHIPPED':
                notifications.send_notification(instance, 'order_shipped')
            elif instance.order_status == 'DELIVERED':
                notifications.send_notification(instance, 'order_delivered')

@receiver(post_save, sender=Order)
def handle_payment_status_change(sender, instance, created, **kwargs):
    notifications = NotificationManager()
    
    if not created and instance.tracker.has_changed('payment_status'):
        if instance.payment_status == 'PAID':
            notifications.send_notification(instance, 'payment_successful')
        elif instance.payment_status == 'FAILED':
            notifications.send_notification(instance, 'payment_failed')

@receiver(pre_save, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    instance.subtotal = instance.price * instance.quantity
