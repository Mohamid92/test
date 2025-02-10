from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Order, PaymentLog
from .payment_gateways.factory import PaymentGatewayFactory

@csrf_exempt
@require_POST
def payment_webhook(request, gateway_name):
    """
    Handle payment webhooks from various payment gateways
    """
    try:
        # Get the payment gateway handler
        gateway = PaymentGatewayFactory.get_gateway(gateway_name)
        
        # Parse webhook data
        webhook_data = json.loads(request.body)
        
        # Validate webhook signature if available
        if not gateway.verify_webhook_signature(request):
            return HttpResponse(status=400)
        
        # Process the webhook
        payment_id = gateway.get_payment_id_from_webhook(webhook_data)
        payment_status = gateway.get_payment_status_from_webhook(webhook_data)
        
        # Update payment log
        payment_log = PaymentLog.objects.filter(payment_id=payment_id).first()
        if payment_log:
            payment_log.status = payment_status
            payment_log.response_data = webhook_data
            payment_log.save()
            
            # Update order status
            order = payment_log.order
            if payment_status == 'SUCCESS':
                order.payment_status = 'PAID'
                order.save()
            elif payment_status == 'FAILED':
                order.payment_status = 'FAILED'
                order.save()
        
        return HttpResponse(status=200)
        
    except Exception as e:
        # Log the error
        print(f"Webhook Error: {str(e)}")
        return HttpResponse(status=500)
