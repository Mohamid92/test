"""
Analytics Models

Core models for tracking user behavior, page views, and sales metrics.
Integrates with:
- User authentication
- Product views
- Cart behavior
- Search patterns
"""

from django.db import models
from django.conf import settings
import json

class UserSession(models.Model):
    """
    Tracks user sessions across the platform
    
    Links to:
    - User model (optional)
    - Page views
    - Product views
    - Cart actions
    """
    session_id = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    device_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

class PageView(models.Model):
    """
    Tracks individual page views
    
    Used for:
    - Traffic analysis
    - User journey mapping
    - Conversion tracking
    """
    session_id = models.CharField(max_length=40, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    url = models.URLField(max_length=500)
    path = models.CharField(max_length=500)
    referrer = models.URLField(max_length=500, null=True)
    device_type = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['path'])
        ]

class ProductView(models.Model):
    """
    Product View Tracking
    
    Records product page views and duration.
    Used for:
    - Product popularity metrics
    - Recommendation engine
    - Conversion tracking
    """
    session_id = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(
        default=0,
        help_text="Time spent viewing in seconds"
    )

    class Meta:
        indexes = [
            models.Index(fields=['product', 'viewed_at']),
            models.Index(fields=['session_id'])
        ]

class CartAbandonment(models.Model):
    """
    Cart Abandonment Tracking
    
    Records abandoned carts for analysis.
    Used by:
    - Marketing automation
    - Sales recovery
    - Customer engagement
    """
    cart = models.ForeignKey('cart.Cart', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    abandoned_at = models.DateTimeField(auto_now_add=True)
    cart_value = models.DecimalField(max_digits=10, decimal_places=2)
    items_count = models.IntegerField()
    recovered = models.BooleanField(default=False)
    recovery_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['abandoned_at']),
            models.Index(fields=['cart_value'])
        ]

class UserBehavior(models.Model):
    BEHAVIOR_TYPES = [
        ('CLICK', 'Click Event'),
        ('SCROLL', 'Scroll Event'),
        ('SEARCH', 'Search Query'),
        ('FILTER', 'Filter Usage'),
        ('SORT', 'Sort Usage')
    ]
    
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPES)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=500)

class SearchQuery(models.Model):
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    results_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('products.Category', null=True, on_delete=models.SET_NULL)

class HeatmapData(models.Model):
    page_url = models.CharField(max_length=500)
    coordinates = models.JSONField()  # Stores x, y coordinates of clicks
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    device_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class InteractionMetrics(models.Model):
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    page_url = models.CharField(max_length=500)
    time_spent = models.IntegerField()  # Time in seconds
    scroll_depth = models.IntegerField()  # Percentage scrolled
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
