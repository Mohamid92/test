from django.utils import timezone
from ..models import PaymentLog, Refund, PaymentAnalytics
from .factory import PaymentGatewayFactory

class RefundManager:
    @staticmethod
    def initiate_refund(order, amount, reason, user):
        payment_log = order.payment_logs.filter(status='SUCCESS').last()
        if not payment_log:
            raise ValueError("No successful payment found for this order")

        refund = Refund.objects.create(
            order=order,
            amount=amount,
            reason=reason,
            status='PENDING'
        )

        gateway = PaymentGatewayFactory.get_gateway(payment_log.gateway)
        
        try:
            result = gateway.process_refund(payment_log.payment_id, amount)
            if result.get('status') == 'success':
                refund.status = 'PROCESSED'
                refund.processed_by = user
                refund.processed_at = timezone.now()
                refund.save()
                
                # Update order status
                order.payment_status = 'REFUNDED'
                order.save()
                
                # Update analytics
                analytics, _ = PaymentAnalytics.objects.get_or_create(
                    date=timezone.now().date()
                )
                analytics.refund_amount += amount
                analytics.save()
                
                return True, "Refund processed successfully"
            
            return False, result.get('message', 'Refund processing failed')
            
        except Exception as e:
            refund.status = 'REJECTED'
            refund.notes = str(e)
            refund.save()
            return False, str(e)
