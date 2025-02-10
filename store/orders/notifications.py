"""
Order Notification System

Handles all order-related notifications via email, SMS, and push notifications.
Integrates with:
- Email backend
- SMS gateway
- Push notification service
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .tasks import send_sms_notification
from .models import StoreConfiguration

class BaseNotificationManager:
    """
    Base notification manager with common functionality.
    Supports:
    - Email notifications
    - SMS notifications
    - Push notifications
    """
    @staticmethod
    def send_email(to_email, subject, template, context):
        """Sends templated emails"""
        html_content = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False
        )

    @staticmethod
    def send_sms(phone_number, message):
        """Queues SMS notifications"""
        send_sms_notification.delay(phone_number, message)

class OrderNotificationManager(BaseNotificationManager):
    """
    Handles order-specific notifications.
    Notifications for:
    - Order confirmation
    - Status updates
    - Shipping updates
    - Delivery confirmation
    """
    @classmethod
    def send_order_confirmation(cls, order):
        """Sends order confirmation notifications"""
        # Email notification
        cls.send_email(
            to_email=order.user.email,
            subject=f'Order Confirmation #{order.order_number}',
            template='orders/emails/order_confirmation.html',
            context={'order': order}
        )
        
        # SMS notification
        message = f'Your order #{order.order_number} has been confirmed. Track at: {settings.SITE_URL}/orders/{order.order_number}'
        cls.send_sms(order.phone_number, message)

    @classmethod
    def notify_status_change(cls, order):
        """Notifies customer of order status changes"""
        # ... notification logic for status changes ...

class PaymentNotificationManager(BaseNotificationManager):
    """
    Handles payment-related notifications.
    Notifications for:
    - Payment confirmation
    - Payment failure
    - Refund status
    """
    @classmethod
    def send_payment_receipt(cls, payment):
        """Sends payment confirmation and receipt"""
        # ... payment notification logic ...

    @classmethod
    def send_refund_approval(cls, refund):
        """Notifies customer of refund approval"""
        # ... refund notification logic ...
