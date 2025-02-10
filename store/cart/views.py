"""
Cart Views

Handles all cart-related operations and API endpoints.
Integrates with:
- Product app for stock validation
- Analytics app for cart tracking
- Authentication for user identification
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from analytics.tracking import UserTracker

class CartViewSet(viewsets.ModelViewSet):
    """
    Cart ViewSet
    
    Handles cart operations including:
    - Cart creation/retrieval
    - Adding/removing items
    - Updating quantities
    - Cart merging for guest users
    """
    serializer_class = CartSerializer
    
    def get_permissions(self):
        """Allow anonymous users to create/retrieve cart"""
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Returns cart for current user or session.
        Integrates with:
        - User authentication
        - Session management
        """
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.filter(session_id=self.request.session.session_key)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add item to cart.
        Integrates with:
        - Product stock management
        - Analytics tracking
        """
        cart = self._get_or_create_cart()
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                item = cart.items.create(**serializer.validated_data)
                # Track cart activity
                UserTracker(request).track_cart_update(cart)
                return Response(CartItemSerializer(item).data)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """
        Update item quantity.
        Validates:
        - Stock availability
        - Minimum quantity
        """
        cart = self._get_or_create_cart()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity > 0:
            item.quantity = quantity
            item.save()
            return Response(CartItemSerializer(item).data)
        
        return Response(
            {'error': 'Quantity must be greater than 0'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self._get_or_create_cart()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_or_create_cart(self):
        """
        Helper method to get or create cart.
        Handles:
        - Authenticated users
        - Guest users with session
        - Cart merging
        """
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            # Merge with session cart if exists
            session_id = self.request.session.session_key
            if session_id:
                session_cart = Cart.objects.filter(session_id=session_id).first()
                if session_cart:
                    cart.merge_with(session_cart)
            return cart
        
        session_id = self.request.session.session_key or self.request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        return cart
