"""
Product Serializers

Handles data serialization/deserialization for the products app.
Used by:
- API views in products.views
- Cart operations
- Order processing
"""

from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductSpecification

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images.
    Used in:
    - ProductSerializer for nested image data
    - Product detail API responses
    - Admin API for image management
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer for product specifications.
    Used in:
    - ProductSerializer for nested specification data
    - Product comparison features
    - Product detail pages
    """
    class Meta:
        model = ProductSpecification
        fields = ['id', 'name', 'value']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories.
    Used in:
    - Category API endpoints
    - Product listing filters
    - Navigation menus
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'is_active', 'is_featured', 'children', 'product_count',
            'meta_description', 'meta_keywords'
        ]

    def get_children(self, obj):
        """Returns serialized child categories if any exist"""
        if (obj.children.exists()):
            return CategorySerializer(obj.children.all(), many=True).data
        return []

    def get_product_count(self, obj):
        """Returns the count of active products in this category"""
        return obj.products.filter(is_active=True).count()

class ProductSerializer(serializers.ModelSerializer):
    """
    Main product serializer.
    Used in:
    - Product API endpoints
    - Cart operations
    - Order processing
    - Product search results
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'category', 'category_id',
            'description', 'short_description', 'price', 'sale_price',
            'stock', 'brand', 'image', 'images', 'specifications',
            'is_active', 'created_at', 'updated_at',
            'meta_description', 'meta_keywords'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
