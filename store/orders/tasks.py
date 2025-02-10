"""
Order Processing Tasks

Celery tasks for asynchronous order processing.
Handles notifications, payments, and inventory updates.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Order, PaymentLog
from .notifications import OrderNotificationManager

@shared_task
def process_order(order_id):
    """Process new order"""
    order = Order.objects.get(id=order_id)
    
    # Update inventory
    for item in order.items.all():
        product = item.product
        product.stock -= item.quantity
        product.save()

    # Send notifications
    OrderNotificationManager.send_order_confirmation(order)
    return True

@shared_task
def check_pending_payments():
    """Check and update pending payment status"""
    timeout = timezone.now() - timezone.timedelta(hours=1)
    pending_payments = PaymentLog.objects.filter(
        status='INITIATED',
        created_at__lt=timeout
    )
    
    for payment in pending_payments:
        try:
            gateway = PaymentGatewayFactory.get_gateway(payment.gateway)
            status = gateway.verify_payment(payment.payment_id)
            
            if status.get('status') in ['SUCCESS', 'FAILED']:
                payment.status = status['status']
                payment.save()
                
                if status['status'] == 'SUCCESS':
                    process_successful_payment.delay(payment.id)
        except Exception as e:
            print(f"Error checking payment {payment.id}: {str(e)}")

@shared_task
def process_successful_payment(payment_id):
    """Handle successful payment processing"""
    payment = PaymentLog.objects.get(id=payment_id)
    order = payment.order
    
    order.payment_status = 'PAID'
    order.order_status = 'PROCESSING'
    order.save()
    
    # Send confirmation
    OrderNotificationManager.send_payment_confirmation(payment)
