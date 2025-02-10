"""
Product Admin Configuration

Customizes the Django admin interface for the products app.
Provides:
- Rich text editing for descriptions
- Inline editing for images and specifications
- Custom filters and search
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductImage, ProductSpecification

class ProductImageInline(admin.TabularInline):
    """
    Inline editor for product images.
    Allows multiple image upload and ordering.
    """
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        """Shows image preview in admin"""
        if obj.image:
            return format_html('<img src="{}" height="50"/>', obj.image)
        return "No Image"

class ProductSpecificationInline(admin.TabularInline):
    """
    Inline editor for product specifications.
    Allows adding technical details to products.
    """
    model = ProductSpecification
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for categories.
    Features:
    - Hierarchical display of categories
    - Slug auto-generation
    - Image preview
    """
    list_display = ['name', 'slug', 'parent', 'is_active', 'is_featured', 'order']
    list_filter = ['is_active', 'is_featured']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'order']
    ordering = ['order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for products.
    Features:
    - Rich text editing
    - Image management
    - Stock tracking
    - Price history
    """
    list_display = [
        'name', 'sku', 'category', 'price', 
        'sale_price', 'stock', 'is_active'
    ]
    list_filter = ['category', 'brand', 'is_active']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'category')
        }),
        ('Details', {
            'fields': ('description', 'short_description', 'brand', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
