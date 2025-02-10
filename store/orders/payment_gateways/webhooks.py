import hmac
import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Order, StoreConfiguration
from .factory import PaymentGatewayFactory

@csrf_exempt
@require_POST
def payment_webhook(request, gateway_name):
    config = StoreConfiguration.objects.first()
    
    # Verify webhook signature
    if not verify_webhook_signature(request, config, gateway_name):
        return HttpResponse(status=400)

    try:
        gateway = PaymentGatewayFactory.get_gateway(gateway_name)
        success = gateway.process_webhook(request.POST.dict())
        
        if success:
            return HttpResponse(status=200)
        return HttpResponse(status=400)
        
    except Exception as e:
        return HttpResponse(status=500)

def verify_webhook_signature(request, config, gateway_name):
    if gateway_name == 'QPAY':
        return verify_qpay_signature(request, config)
    elif gateway_name == 'CBQ':
        return verify_cbq_signature(request, config)
    def verify_cbq_signature(request, config):
        signature = request.headers.get('X-Signature')
        if not signature:
            return False
        
        # Calculate expected signature
        data = request.POST.dict()
        message = ''.join([str(v) for v in sorted(data.values())]) + config.cbq_secret_key
        expected = hashlib.sha256(message.encode()).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
        # Add more gateway signature verifications
    return False

def verify_qpay_signature(request, config):
    signature = request.headers.get('X-Signature')
    if not signature:
        return False
    
    # Calculate expected signature
    data = request.POST.dict()
    message = ''.join([str(v) for v in sorted(data.values())]) + config.qpay_secret_key
    expected = hashlib.sha256(message.encode()).hexdigest()
    
    return hmac.compare_digest(signature, expected)
