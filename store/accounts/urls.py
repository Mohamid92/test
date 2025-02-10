"""
Account URLs Configuration

Defines URL patterns for user management.
Integrates with DRF router and authentication system.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')

app_name = 'accounts'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Authentication endpoints
    path('api/auth/', include('rest_framework.urls')),
]

# Generated URL patterns:
# /api/users/ - User listing (admin only)
# /api/users/register/ - User registration
# /api/users/verify_phone/ - Phone verification
# /api/addresses/ - Address management
# /api/addresses/{pk}/set_default/ - Set default address
