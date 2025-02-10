from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import requests
from .models import StoreConfiguration

class NotificationManager:
    EMAIL_TEMPLATES = {
        'order_confirmation': 'emails/order_confirmation.html',
        'order_shipped': 'emails/order_shipped.html',
        'order_delivered': 'emails/order_delivered.html',
        'payment_successful': 'emails/payment_successful.html',
        'payment_failed': 'emails/payment_failed.html'
    }

    def __init__(self):
        self.config = StoreConfiguration.objects.first()

    def send_notification(self, order, notification_type):
        if self.config.enable_order_emails:
            self._send_email(order, notification_type)
        if self.config.enable_sms_notifications:
            self._send_sms(order, notification_type)

    def _send_email(self, order, notification_type):
        template = self.EMAIL_TEMPLATES.get(notification_type)
        if not template:
            return False

        subject = f"{notification_type.replace('_', ' ').title()} - Order #{order.order_number}"
        context = {
            'order': order,
            'config': self.config
        }

        message = render_to_string(template, context)
        recipient = order.user.email if order.user else order.phone_number

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=self.config.from_email,
            to=[recipient],
            reply_to=[self.config.admin_email]
        )
        email.content_subtype = "html"
        return email.send()

    def _send_sms(self, order, notification_type):
        message = self._get_sms_message(order, notification_type)
        if self.config.sms_provider == 'OOREDOO':
            return self._send_ooredoo_sms(order.phone_number, message)
        return False

    def _get_sms_message(self, order, notification_type):
        messages = {
            'order_confirmation': f"Order #{order.order_number} confirmed. Total: QAR {order.total_amount}",
            'order_shipped': f"Order #{order.order_number} shipped. Track: {order.tracking_number}",
            'order_delivered': f"Order #{order.order_number} delivered. Thank you!",
            'payment_successful': f"Payment received for order #{order.order_number}",
            'payment_failed': f"Payment failed for order #{order.order_number}. Please try again."
        }
        return messages.get(notification_type, '')
