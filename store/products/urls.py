"""
Product URL Configuration

Defines URL patterns for the products app.
Integrates with:
- DRF router for API endpoints
- Frontend templates
- SEO-friendly URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

app_name = 'products'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),

    # Frontend URLs - handled by TemplateView in main urls.py
    # Listed here for documentation purposes
    # path('', product_list, name='product-list'),
    # path('<slug:slug>/', product_detail, name='product-detail'),
    # path('category/<slug:slug>/', category_detail, name='category-detail'),
]

# URL patterns created by the router:
# - /api/products/
# - /api/products/{pk}/
# - /api/categories/
# - /api/categories/{slug}/
