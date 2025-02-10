"""
Product Management Models

This module contains the core models for product management in the e-commerce system.
These models are fundamental and are referenced by many other apps including:
- cart (for shopping cart items)
- orders (for order items)
- analytics (for product views and metrics)
"""

from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """
    Product Category Model
    
    Represents product categories in a hierarchical structure.
    Related to:
    - Product model (one-to-many)
    - Self (for parent-child relationships)
    - Used in analytics.SearchQuery for category-specific searches
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200, 
        unique=True,
        help_text="URL-friendly version of the category name"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent category if this is a subcategory"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the category"
    )
    meta_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Meta description for SEO"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Meta keywords for SEO"
    )
    image = models.URLField(
        max_length=500,
        blank=True,
        help_text="Category image URL"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order of the category"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active and should be displayed"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this category should be featured on the homepage"
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order']

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from name.
        Called by:
        - Admin interface
        - API views
        - Management commands
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the URL for the category page.
        Used by:
        - Templates for generating links
        - Sitemap generation
        - SEO app for URL management
        """
        return f"/categories/{self.slug}/"

class Product(models.Model):
    """
    Product Model
    
    Core product information used throughout the system.
    Related to:
    - Category (many-to-one)
    - CartItem (one-to-many)
    - OrderItem (one-to-many)
    - ProductView in analytics (one-to-many)
    """
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    short_description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    brand = models.CharField(max_length=100)
    meta_description = models.CharField(max_length=255, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.URLField(max_length=500, blank=True)  # Added image field as URLField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    """
    Product Images Model
    
    Stores multiple images for a single product.
    Related to:
    - Product (many-to-one)
    Used in:
    - Product detail templates
    - API responses for product details
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.URLField(max_length=500)  # Changed to URLField for external images
    alt_text = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductSpecification(models.Model):
    """
    Product Specifications Model
    
    Stores technical specifications for products.
    Related to:
    - Product (many-to-one)
    Used in:
    - Product detail pages
    - Product comparison features
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.product.name}"
