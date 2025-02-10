"""
Order Model Managers

Custom model managers for order-related models.
Provides common query operations and business logic.
"""

from django.db import models
from django.utils import timezone

class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(order_status='PENDING')

    def processing(self):
        return self.filter(order_status='PROCESSING')

    def completed(self):
        return self.filter(order_status__in=['DELIVERED', 'CANCELLED'])

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def create_from_cart(self, cart, address, phone_number):
        """Create new order from cart items"""
        order = self.create(
            user=cart.user,
            shipping_address=address,
            phone_number=phone_number,
            total_amount=cart.total
        )
        
        # Create order items
        for cart_item in cart.items.all():
            order.items.create(
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        return order
