"""
Base Payment Gateway

Abstract base class for payment gateway implementations.
Provides common functionality and required methods.
"""

from abc import ABC, abstractmethod
import hmac
import hashlib
import json
from django.conf import settings
from ..models import Order, StoreConfiguration

class BasePaymentGateway(ABC):
    """
    Abstract base class for payment gateways
    All gateway implementations must extend this
    """

    def __init__(self):
        self.config = StoreConfiguration.objects.first()

    @abstractmethod
    def initiate_payment(self, order: Order) -> dict:
        """Initialize payment process"""
        pass

    @abstractmethod
    def verify_payment(self, payment_id: str) -> dict:
        """Verify payment status"""
        pass

    @abstractmethod
    def process_refund(self, payment_id: str, amount: float) -> dict:
        """Process refund request"""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: dict, signature: str) -> bool:
        """Verify webhook signature"""
        pass

    def generate_signature(self, data: dict, secret: str) -> str:
        """Generate HMAC signature for data"""
        message = json.dumps(data, sort_keys=True)
        return hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def log_payment(self, order: Order, payment_id: str, status: str, response_data: dict) -> None:
        """Log payment transaction"""
        from ..models import PaymentLog
        return PaymentLog.objects.create(
            order=order,
            payment_id=payment_id,
            gateway=self.__class__.__name__.replace('Gateway', '').upper(),
            amount=order.total_amount,
            status=status,
            response_data=response_data
        )
