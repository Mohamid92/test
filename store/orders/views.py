"""
Order Management Views

Handles order processing, payments, and analytics.
Integrates with:
- Payment gateways
- Inventory management
- Customer notifications
- Analytics tracking
"""

from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Order, PaymentLog
from .serializers import OrderSerializer, OrderCreateSerializer
from .payment_gateways.factory import PaymentGatewayFactory
from .tasks import process_order, send_order_notification

class OrderViewSet(viewsets.ModelViewSet):
    """
    Order management viewset
    
    Handles:
    - Order creation and updates
    - Payment processing
    - Order cancellation
    - Refunds
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter orders by user"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Process payment for order
        
        Steps:
        1. Validate order status
        2. Initialize payment gateway
        3. Process payment
        4. Update order status
        5. Send notifications
        """
        order = self.get_object()
        gateway_name = request.data.get('gateway')
        
        try:
            gateway = PaymentGatewayFactory.get_gateway(gateway_name)
            result = gateway.process_payment(order, request.data)
            
            if result.get('status') == 'success':
                order.payment_status = 'PAID'
                order.save()
                process_order.delay(order.id)
            
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel order if eligible
        
        Checks:
        - Order status
        - Payment status
        - Time constraints
        """
        order = self.get_object()
        if not order.can_cancel:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.order_status = 'CANCELLED'
        order.save()
        
        # Send cancellation notification
        send_order_notification.delay(order.id, 'CANCELLED')
        return Response({'status': 'order cancelled'})

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        config = StoreConfiguration.objects.first()
        
        if not config.enable_online_payment:
            return Response(
                {'error': 'Online payment is not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            gateway = PaymentGatewayFactory.get_gateway(config.payment_gateway)
            result = gateway.initiate_payment(order)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        order = self.get_object()
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'Payment ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        config = StoreConfiguration.objects.first()
        try:
            gateway = PaymentGatewayFactory.get_gateway(config.payment_gateway)
            result = gateway.verify_payment(payment_id)
            
            if result.get('status') == 'success':
                order.payment_status = 'PAID'
                order.save()
                
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        order = self.get_object()
        amount = request.data.get('amount')
        reason = request.data.get('reason')
        
        if not amount or not reason:
            return Response(
                {'error': 'Amount and reason are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        success, message = RefundManager.initiate_refund(
            order, amount, reason, request.user
        )
        
        if success:
            return Response({'message': message})
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        analytics = PaymentAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        return Response(PaymentAnalyticsSerializer(analytics, many=True).data)

class PaymentWebhookView(views.APIView):
    """
    Payment webhook handler
    
    Processes:
    - Payment gateway callbacks
    - Order status updates
    - Payment verification
    """
    
    def post(self, request, gateway_name):
        try:
            gateway = PaymentGatewayFactory.get_gateway(gateway_name)
            result = gateway.handle_webhook(request)
            
            if result.get('order_id'):
                order = Order.objects.get(id=result['order_id'])
                if result.get('status') == 'success':
                    order.payment_status = 'PAID'
                    order.save()
                    process_order.delay(order.id)
            
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentReconciliationView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        gateway = request.query_params.get('gateway')

        payment_logs = PaymentLog.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        if gateway:
            payment_logs = payment_logs.filter(gateway=gateway)

        reconciliation_data = {
            'total_transactions': payment_logs.count(),
            'successful_transactions': payment_logs.filter(status='SUCCESS').count(),
            'failed_transactions': payment_logs.filter(status='FAILED').count(),
            'total_amount': payment_logs.filter(status='SUCCESS').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'refunded_amount': payment_logs.filter(status='REFUNDED').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'transactions_by_gateway': payment_logs.values('gateway').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
        }

        return Response(reconciliation_data)
