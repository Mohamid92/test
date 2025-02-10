import hashlib
import requests
from django.conf import settings
from ..models import StoreConfiguration

class QPayGateway:
    def __init__(self):
        self.config = StoreConfiguration.objects.first()
        self.merchant_id = self.config.qpay_merchant_id
        self.secret_key = self.config.qpay_secret_key
        self.api_url = self.config.qpay_api_url

    def generate_signature(self, data):
        string_to_hash = ''.join([str(v) for v in sorted(data.items())]) + self.secret_key
        return hashlib.sha256(string_to_hash.encode()).hexdigest()

    def initiate_payment(self, order):
        payload = {
            'merchantId': self.merchant_id,
            'orderId': order.order_number,
            'amount': str(order.total_amount),
            'currency': 'QAR',
            'language': 'en',
            'returnUrl': f'{settings.SITE_URL}/payment/qpay/callback/',
            'customerEmail': order.user.email if order.user else '',
            'customerMobile': order.phone_number
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.generate_signature(payload)
        }
        
        response = requests.post(f'{self.api_url}/pg/checkout', json=payload, headers=headers)
        return response.json()
