"""
Payment Gateway Webhooks

Handles incoming webhook requests from payment gateways.
Integrates with:
- Payment analytics
- Order status updates
- Customer notifications
"""

import json
import hmac
import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order, PaymentLog
from .utils import validate_payment_signature, update_payment_analytics
from django.conf import settings

@csrf_exempt
@require_POST
def payment_webhook(request, gateway_name):
    """
    Generic payment webhook handler.
    Supports multiple payment gateways through factory pattern.
    """
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Payment-Signature')
        if not validate_payment_signature(request.body, signature, gateway_name):
            return HttpResponse(status=400)

        # Parse webhook data
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        # Update payment log
        payment_log = PaymentLog.objects.filter(payment_id=payment_id).first()
        if payment_log:
            payment_log.status = data.get('status')
            payment_log.response_data = data
            payment_log.save()
            
            # Update analytics
            update_payment_analytics(payment_log)
            
            # Update order status
            order = payment_log.order
            if data.get('status') == 'SUCCESS':
                order.payment_status = 'PAID'
                order.save()
                
                # Send confirmation
                from .tasks import send_payment_confirmation
                send_payment_confirmation.delay(order.id)
        
        return HttpResponse(status=200)
        
    except Exception as e:
        import logging
        logging.error(f"Webhook Error: {str(e)}")
        return HttpResponse(status=500)

# Specific gateway handlers
@csrf_exempt
@require_POST
def handle_qpay_webhook(request):
    """QPay specific webhook handler"""
    return payment_webhook(request, 'QPAY')

@csrf_exempt
@require_POST
def handle_cbq_webhook(request):
    """CBQ specific webhook handler"""
    return payment_webhook(request, 'CBQ')

@csrf_exempt
@require_POST
def handle_naps_webhook(request):
    """NAPS specific webhook handler"""
    return payment_webhook(request, 'NAPS')

@csrf_exempt
@require_POST
def handle_tap_webhook(request):
    """Tap Payments specific webhook handler"""
    return payment_webhook(request, 'TAP')
