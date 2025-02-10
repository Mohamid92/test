from .qpay import QPayGateway
from .cbq import CBQGateway
from .naps import NAPSGateway
from .qnb import QNBGateway
from .tap import TapGateway
from .fatoora import FatooraGateway

class PaymentGatewayFactory:
    GATEWAYS = {
        'QPAY': QPayGateway,
        'CBQ': CBQGateway,
        'NAPS': NAPSGateway,
        'QNB': QNBGateway,
        'TAP': TapGateway,
        'FATOORA': FatooraGateway,
    }

    @classmethod
    def get_gateway(cls, gateway_name: str):
        gateway_class = cls.GATEWAYS.get(gateway_name.upper())
        if not gateway_class:
            raise ValueError(f"Unsupported payment gateway: {gateway_name}")
        return gateway_class()
