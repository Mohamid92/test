from abc import ABC, abstractmethod
from ..models import Order, StoreConfiguration

class PaymentGateway(ABC):
    def __init__(self):
        self.config = StoreConfiguration.objects.first()

    @abstractmethod
    def initiate_payment(self, order: Order) -> dict:
        pass

    @abstractmethod
    def verify_payment(self, payment_id: str) -> dict:
        pass

    @abstractmethod
    def process_webhook(self, request_data: dict) -> bool:
        pass
