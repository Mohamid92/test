"""
Cart Serializers

Handles serialization of cart data for API responses.
Used by cart views and order processing.
"""

from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """
    Cart Item Serializer
    
    Used in:
    - Cart API responses
    - Cart item management
    - Order creation
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id',
            'quantity', 'subtotal', 'added_at'
        ]
        read_only_fields = ['subtotal', 'added_at']

    def validate_quantity(self, value):
        """Ensures quantity is positive and within stock limits"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        """
        Validates stock availability.
        Called during cart item creation/update.
        """
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        from products.models import Product
        try:
            product = Product.objects.get(id=product_id)
            if quantity > product.stock:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available in stock."
                )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
            
        return data

class CartSerializer(serializers.ModelSerializer):
    """
    Cart Serializer
    
    Main serializer for cart operations.
    Used in:
    - Cart API endpoints
    - Checkout process
    - Cart management
    """
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
