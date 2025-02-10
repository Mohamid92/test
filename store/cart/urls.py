"""
Cart URLs Configuration

Defines URL patterns for cart operations.
Integrates with:
- DRF router for API endpoints
- Frontend templates
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

app_name = 'cart'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]

# URL patterns created by router:
# - /api/cart/
# - /api/cart/{pk}/
# - /api/cart/add_item/
# - /api/cart/update_quantity/
# - /api/cart/clear/
