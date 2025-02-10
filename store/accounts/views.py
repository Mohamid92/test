"""
Account Views

Handles user-related operations and API endpoints.
Integrates with authentication, cart, and order systems.
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, login
from .serializers import UserSerializer, UserRegistrationSerializer, PhoneVerificationSerializer, AddressSerializer
from .models import Address
from cart.models import Cart

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset.
    Handles:
    - User registration
    - Profile management
    - Address management
    - Cart association
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'verify_phone']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        User registration endpoint.
        Integrates with:
        - Phone verification system
        - Cart merging for guest users
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Associate guest cart if exists
            session_id = request.session.session_key
            if session_id:
                guest_cart = Cart.objects.filter(session_id=session_id).first()
                if guest_cart:
                    guest_cart.user = user
                    guest_cart.session_id = None
                    guest_cart.save()

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_phone(self, request):
        """
        Phone verification endpoint.
        Used for:
        - New user verification
        - Password reset verification
        """
        phone = request.data.get('phone_number')
        code = request.data.get('code')
        
        user = User.objects.filter(phone_number=phone).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify code logic here
        user.is_verified = True
        user.save()
        return Response({'status': 'verified'})

class AddressViewSet(viewsets.ModelViewSet):
    """
    Address management viewset.
    Used for:
    - Managing shipping addresses
    - Managing billing addresses
    - Default address selection
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Sets an address as default for the user"""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'status': 'default address updated'})
