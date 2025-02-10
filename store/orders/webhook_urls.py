"""
Payment Webhook URLs

Handles webhook endpoints for different payment gateways.
Used by:
- Payment gateway callbacks
- Payment status updates
- Order status management
"""

from django.urls import path
from .webhooks import (
    handle_qpay_webhook,
    handle_cbq_webhook,
    handle_naps_webhook,
    handle_tap_webhook
)

urlpatterns = [
    path('qpay/', handle_qpay_webhook, name='qpay-webhook'),
    path('cbq/', handle_cbq_webhook, name='cbq-webhook'),
    path('naps/', handle_naps_webhook, name='naps-webhook'),
    path('tap/', handle_tap_webhook, name='tap-webhook'),
]
