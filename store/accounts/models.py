"""
Account Management Models

Handles user authentication, profile management, and addresses.
Integrates with:
- Cart app for user cart association
- Orders app for shipping addresses
- Analytics for user behavior tracking
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for phone number authentication.
    Used by:
    - User model
    - Authentication backend
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User Model
    
    Uses phone number as primary identifier.
    Related to:
    - Cart for shopping sessions
    - Orders for purchase history
    - Addresses for shipping/billing
    """
    username = None  # Remove username field
    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(_('email address'), blank=True)
    is_verified = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email'])
        ]

class Address(models.Model):
    """
    User Address Model
    
    Stores shipping and billing addresses.
    Used by:
    - Order processing
    - User profile management
    - Checkout process
    """
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    is_billing = models.BooleanField(default(False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]

    def save(self, *args, **kwargs):
        """Ensures only one default address per user"""
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
