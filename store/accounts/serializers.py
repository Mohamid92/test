from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'city', 'state', 'postal_code', 'is_default']

class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'email', 'first_name', 'last_name', 'is_verified', 'addresses']
        read_only_fields = ['is_verified']

class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
