"""
Payment Gateway Factory

Provides a factory pattern implementation for different payment gateways.
Integrates with:
- Gateway configurations
- Payment processing
- Response handling
"""

from django.conf import settings
from .qpay import QPAYGateway
from .cbq import CBQGateway
from .naps import NAPSGateway
from .tap import TAPGateway
from .ooredoo import OoredooGateway
from .fatoora import FatooraGateway

class PaymentGatewayFactory:
    """
    Factory class for payment gateway initialization
    """
    
    GATEWAYS = {
        'QPAY': QPAYGateway,
        'CBQ': CBQGateway,
        'NAPS': NAPSGateway,
        'TAP': TAPGateway,
        'OOREDOO': OoredooGateway,
        'FATOORA': FatooraGateway
    }

    @classmethod
    def get_gateway(cls, gateway_name):
        """Returns configured gateway instance"""
        if gateway_name not in cls.GATEWAYS:
            raise ValueError(f"Unsupported gateway: {gateway_name}")
            
        gateway_class = cls.GATEWAYS[gateway_name]
        return gateway_class()
