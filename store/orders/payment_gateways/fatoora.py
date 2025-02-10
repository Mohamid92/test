from .base import PaymentGateway
import requests
import base64
from datetime import datetime
from django.conf import settings
from ..models import StoreConfiguration, PaymentLog

class FatooraGateway(PaymentGateway):
    def __init__(self):
        super().__init__()
        self.config = StoreConfiguration.objects.first()
        self.api_url = "https://api.fatoora.qa/v2"

    def generate_qr_data(self, order):
        data = {
            'seller': settings.STORE_NAME,
            'vat': settings.VAT_NUMBER,
            'datetime': datetime.now().isoformat(),
            'total': str(order.total_amount),
            'tax': str(order.total_amount * 0.15)
        }
        return base64.b64encode(str(data).encode()).decode()

    def initiate_payment(self, order):
        payload = {
            'amount': float(order.total_amount),
            'currency': 'QAR',
            'customer_email': order.user.email if order.user else '',
            'customer_phone': order.phone_number,
            'order_number': order.order_number,
            'qr_data': self.generate_qr_data(order),
            'callback_url': f'{settings.SITE_URL}/payment/callback/fatoora/'
        }

        headers = {
            'Authorization': f'Bearer {self.config.fatoora_api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f"{self.api_url}/payment/init",
            json=payload,
            headers=headers
        )

        PaymentLog.objects.create(
            order=order,
            payment_id=response.json().get('payment_id'),
            gateway='FATOORA',
            amount=order.total_amount,
            status='INITIATED',
            response_data=response.json()
        )

        return response.json()

    def verify_payment(self, payment_id):
        headers = {
            'Authorization': f'Bearer {self.config.fatoora_api_key}'
        }
        
        response = requests.get(
            f"{self.api_url}/payment/status/{payment_id}",
            headers=headers
        )
        return response.json()

    def process_webhook(self, request_data):
        payment_id = request_data.get('payment_id')
        status = request_data.get('status')
        
        payment_log = PaymentLog.objects.get(payment_id=payment_id)
        payment_log.status = 'SUCCESS' if status == 'paid' else 'FAILED'
        payment_log.response_data = request_data
        payment_log.save()
        
        if status == 'paid':
            order = payment_log.order
            order.payment_status = 'PAID'
            order.save()
            return True
        return False
