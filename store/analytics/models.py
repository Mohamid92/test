from django.db import models
from django.conf import settings

# Create your models here.

class PageView(models.Model):
    session_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    referrer = models.CharField(max_length=500, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True)
    browser = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductView(models.Model):
    session_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # Time spent viewing in seconds

class CartAbandonment(models.Model):
    cart = models.ForeignKey('cart.Cart', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    abandoned_at = models.DateTimeField(auto_now_add=True)
    cart_value = models.DecimalField(max_digits=10, decimal_places=2)
    items_count = models.IntegerField()

class UserSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    device_info = models.JSONField(default=dict)

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
