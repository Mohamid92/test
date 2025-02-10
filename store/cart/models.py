"""
Cart Management Models

This module handles shopping cart functionality.
Integrates with:
- products app for product information
- orders app for checkout process
- analytics app for cart abandonment tracking
"""

from django.db import models
from django.conf import settings
from products.models import Product
from decimal import Decimal

class Cart(models.Model):
    """
    Shopping Cart Model
    
    Handles both authenticated and guest user carts using either user ID or session ID.
    Related to:
    - User model (optional, for authenticated users)
    - CartItem (one-to-many)
    - Order model (during checkout)
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Optional. Cart can exist with session_id for anonymous users"
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="For tracking guest user carts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id'])
        ]

    @property
    def total(self):
        """
        Calculates cart total.
        Used by:
        - Cart display
        - Checkout process
        - Order creation
        """
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        """
        Returns total number of items in cart.
        Used by:
        - Cart badge in navigation
        - Cart summary
        """
        return self.items.count()

    def merge_with(self, other_cart):
        """
        Merges another cart into this one.
        Used when:
        - Guest user logs in
        - Session cart needs to be merged with user cart
        """
        for item in other_cart.items.all():
            existing_item = self.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        other_cart.delete()

class CartItem(models.Model):
    """
    Cart Item Model
    
    Represents individual items in a cart.
    Related to:
    - Cart model (many-to-one)
    - Product model (many-to-one)
    - Used in order creation
    """
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-added_at']

    @property
    def subtotal(self):
        """
        Calculates item subtotal.
        Considers sale price if available.
        """
        price = self.product.sale_price or self.product.price
        return price * Decimal(str(self.quantity))

    def clean(self):
        """
        Validates item quantity against stock.
        Called before saving to database.
        """
        from django.core.exceptions import ValidationError
        if self.quantity > self.product.stock:
            raise ValidationError(f'Only {self.product.stock} items available in stock.')

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure:
        - Quantity validation
        - Stock availability check
        - Analytics tracking
        """
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update cart timestamp
        self.cart.save()
