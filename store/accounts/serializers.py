"""
Account Serializers

Handles data serialization for user management.
Used in API endpoints and form processing.
"""

from rest_framework import serializers
from .models import User, Address
from django.contrib.auth.password_validation import validate_password

class AddressSerializer(serializers.ModelSerializer):
    """
    Address serializer for shipping/billing addresses.
    Used in:
    - Checkout process
    - User profile management
    """
    class Meta:
        model = Address
        fields = [
            'id', 'street_address', 'apartment', 'city',
            'state', 'postal_code', 'is_default', 'is_billing'
        ]

class UserSerializer(serializers.ModelSerializer):
    """
    Main user serializer for profile management.
    Integrates with:
    - Authentication system
    - Profile management
    - Order processing
    """
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'first_name',
            'last_name', 'is_verified', 'addresses'
        ]
        read_only_fields = ['is_verified']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Used for user registration process.
    Handles:
    - Password validation
    - Phone verification
    - Initial profile setup
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'phone_number', 'email', 'password', 'password2',
            'first_name', 'last_name'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Passwords don't match"
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
