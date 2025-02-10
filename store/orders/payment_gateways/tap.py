from .base import PaymentGateway
import requests
import json
from django.conf import settings
from ..models import StoreConfiguration, PaymentLog

class TapGateway(PaymentGateway):
    def __init__(self):
        super().__init__()
        self.config = StoreConfiguration.objects.first()
        self.api_url = "https://api.tap.company/v2"
        
    def initiate_payment(self, order):
        payload = {
            "amount": float(order.total_amount),
            "currency": "QAR",
            "customer": {
                "first_name": order.user.first_name if order.user else "",
                "phone": {
                    "country_code": "974",
                    "number": order.phone_number
                }
            },
            "source": {"id": "src_all"},
            "redirect": {
                "url": f"{settings.SITE_URL}/payment/callback/tap/"
            },
            "reference": {
                "order": order.order_number
            }
        }

        headers = {
            "authorization": f"Bearer {self.config.tap_secret_key}",
            "content-type": "application/json"
        }

        response = requests.post(
            f"{self.api_url}/charges",
            json=payload,
            headers=headers
        )
        
        PaymentLog.objects.create(
            order=order,
            payment_id=response.json().get('id'),
            gateway='TAP',
            amount=order.total_amount,
            status='INITIATED',
            response_data=response.json()
        )
        
        return response.json()

    def verify_payment(self, payment_id):
        headers = {
            "authorization": f"Bearer {self.config.tap_secret_key}"
        }
        
        response = requests.get(
            f"{self.api_url}/charges/{payment_id}",
            headers=headers
        )
        return response.json()

    def process_webhook(self, request_data):
        charge_id = request_data.get('id')
        status = request_data.get('status')
        
        payment_log = PaymentLog.objects.get(payment_id=charge_id)
        payment_log.status = 'SUCCESS' if status == 'CAPTURED' else 'FAILED'
        payment_log.response_data = request_data
        payment_log.save()
        
        if status == 'CAPTURED':
            order = payment_log.order
            order.payment_status = 'PAID'
            order.save()
            return True
        return False
