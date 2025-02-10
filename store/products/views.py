"""
Product Views and ViewSets

Handles all product-related API endpoints and views.
Integrates with:
- Cart app for adding products to cart
- Analytics app for tracking product views
- SEO app for meta tags
"""

from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from analytics.tracking import UserTracker

class ProductFilter(django_filters.FilterSet):
    """
    Product filtering class
    
    Used by:
    - ProductViewSet
    - API endpoints for filtering products
    - Frontend product listing pages
    """
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr='gte',
        help_text="Filter products with price greater than or equal to this value"
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr='lte',
        help_text="Filter products with price less than or equal to this value"
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        help_text="Filter products by category slug"
    )

    class Meta:
        model = Product
        fields = ['category', 'brand', 'is_active', 'min_price', 'max_price']

class ProductViewSet(viewsets.ModelViewSet):
    """
    Product ViewSet
    
    Handles all product-related API endpoints.
    Integrates with:
    - Analytics app for tracking product views
    - Cart app for checking stock availability
    - Order app for checking product availability
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering_fields = ['created_at', 'price', 'name']
    search_fields = ['name', 'description', 'brand']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
