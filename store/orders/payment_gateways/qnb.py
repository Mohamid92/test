from .base import PaymentGateway
import requests
import hashlib
from django.conf import settings
from ..models import PaymentLog, StoreConfiguration

class QNBGateway(PaymentGateway):
    def __init__(self):
        super().__init__()
        self.config = StoreConfiguration.objects.first()
        self.api_url = "https://qnb.qa/pg/api/v2"

    def generate_signature(self, data):
        signing_string = f"{data['merchantId']}|{data['orderNumber']}|{data['amount']}|{self.config.qnb_secret_key}"
        return hashlib.sha512(signing_string.encode()).hexdigest()

    def initiate_payment(self, order):
        payload = {
            'merchantId': self.config.qnb_merchant_id,
            'orderNumber': order.order_number,
            'amount': str(order.total_amount),
            'currency': 'QAR',
            'customerEmail': order.user.email if order.user else '',
            'customerMobile': order.phone_number,
            'callbackUrl': f'{settings.SITE_URL}/payment/callback/qnb/',
            'language': 'en'
        }
        
        headers = {
            'Authorization': self.generate_signature(payload),
            'Content-Type': 'application/json'
        }

        response = requests.post(f"{self.api_url}/payment/init", json=payload, headers=headers)
        
        # Log the payment attempt
        PaymentLog.objects.create(
            order=order,
            payment_id=response.json().get('paymentId'),
            gateway='QNB',
            amount=order.total_amount,
            status='INITIATED',
            response_data=response.json()
        )
        
        return response.json()

    def verify_payment(self, payment_id):
        payload = {
            'merchantId': self.config.qnb_merchant_id,
            'paymentId': payment_id
        }
        
        headers = {
            'Authorization': self.generate_signature(payload),
            'Content-Type': 'application/json'
        }

        response = requests.post(f"{self.api_url}/payment/verify", json=payload, headers=headers)
        return response.json()

    def process_webhook(self, request_data):
        payment_id = request_data.get('paymentId')
        status = request_data.get('status')
        
        try:
            payment_log = PaymentLog.objects.get(payment_id=payment_id)
            payment_log.status = 'SUCCESS' if status == 'APPROVED' else 'FAILED'
            payment_log.response_data = request_data
            payment_log.save()
            
            if status == 'APPROVED':
                order = payment_log.order
                order.payment_status = 'PAID'
                order.save()
                return True
                
            return False
            
        except PaymentLog.DoesNotExist:
            return False
