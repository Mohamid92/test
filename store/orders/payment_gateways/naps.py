import hashlib
import time
import requests
from django.conf import settings
from ..models import StoreConfiguration

class NAPSGateway:
    def __init__(self):
        self.config = StoreConfiguration.objects.first()
        self.merchant_id = self.config.naps_merchant_id
        self.secret_key = self.config.naps_secret_key
        self.api_url = "https://naps.qa/api"

    def generate_tranportal_id(self):
        return f"NAPS_{self.merchant_id}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"

    def initiate_payment(self, order):
        payload = {
            'merchantId': self.merchant_id,
            'tranportalId': self.generate_tranportal_id(),
            'amount': str(order.total_amount),
            'currency': '634',  # QAR currency code for NAPS
            'action': '1',  # Purchase
            'customerEmail': order.user.email if order.user else '',
            'customerMobile': order.phone_number,
            'responseURL': f'{settings.SITE_URL}/payment/naps/callback/'
        }

        response = requests.post(f'{self.api_url}/initiate', json=payload)
        return response.json()
