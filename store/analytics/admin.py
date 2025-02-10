from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .models import (PageView, ProductView, CartAbandonment, UserSession, 
                    UserBehavior, SearchQuery, HeatmapData, InteractionMetrics)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'device_type', 'created_at')
    list_filter = ('device_type', 'created_at')
    search_fields = ('url', 'user__phone_number')

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'duration', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('product__name', 'user__phone_number')

@admin.register(CartAbandonment)
class CartAbandonmentAdmin(admin.ModelAdmin):
    list_display = ('cart', 'user', 'cart_value', 'items_count', 'abandoned_at')
    list_filter = ('abandoned_at',)
    search_fields = ('user__phone_number',)

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'start_time', 'is_active')
    list_filter = ('is_active', 'start_time')
    search_fields = ('session_id', 'user__phone_number')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('session-analytics/', self.admin_site.admin_view(self.session_analytics_view),
                 name='session-analytics'),
        ]
        return custom_urls + urls

    def session_analytics_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Session Analytics'
        }
        return TemplateResponse(request, "admin/analytics/session_analytics.html", context)

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ('session', 'behavior_type', 'timestamp', 'url')
    list_filter = ('behavior_type', 'timestamp')
    search_fields = ('session__session_id', 'url')

@admin.register(HeatmapData)
class HeatmapDataAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'device_type', 'created_at')
    list_filter = ('device_type', 'created_at')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('heatmap-view/', self.admin_site.admin_view(self.heatmap_view),
                 name='heatmap-view'),
        ]
        return custom_urls + urls

    def heatmap_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Heatmap Visualization'
        }
        return TemplateResponse(request, "admin/analytics/heatmap.html", context)

@admin.register(InteractionMetrics)
class InteractionMetricsAdmin(admin.ModelAdmin):
    list_display = ('session', 'page_url', 'time_spent', 'scroll_depth', 'click_count')
    list_filter = ('created_at',)
    search_fields = ('page_url',)

    def has_add_permission(self, request):
        return False
