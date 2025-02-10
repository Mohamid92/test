from rest_framework import serializers
from .models import Order, OrderItem, PaymentAnalytics
from accounts.serializers import AddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'subtotal']
        read_only_fields = ['subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'phone_number', 'shipping_address',
            'order_status', 'payment_status', 'total_amount', 'items',
            'tracking_number', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['phone_number', 'shipping_address_id', 'items', 'notes']

class PaymentAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAnalytics
        fields = ['date', 'total_amount', 'transaction_count', 'payment_method']
