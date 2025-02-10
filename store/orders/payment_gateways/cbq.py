from django.conf import settings
import requests
from datetime import datetime
import hmac
import hashlib

from ..models import StoreConfiguration

class CBQGateway:
    def __init__(self):
        self.config = StoreConfiguration.objects.first()
        self.merchant_id = self.config.cbq_merchant_id
        self.terminal_id = self.config.cbq_terminal_id
        self.secret_key = self.config.cbq_secret_key
        self.api_url = "https://cbq.qa/payment/api/v1"

    def generate_signature(self, data):
        message = f"{self.merchant_id}|{self.terminal_id}|{data['amount']}|{data['orderNumber']}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def initiate_payment(self, order):
        payload = {
            'merchantId': self.merchant_id,
            'terminalId': self.terminal_id,
            'orderNumber': order.order_number,
            'amount': str(order.total_amount),
            'currency': 'QAR',
            'timestamp': datetime.now().strftime('%Y%m%d%H%M%S'),
            'returnUrl': f'{settings.SITE_URL}/payment/cbq/callback/'
        }
        
        headers = {
            'Authorization': self.generate_signature(payload),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f'{self.api_url}/checkout', json=payload, headers=headers)
        return response.json()
