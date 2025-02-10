"""
Analytics URL Configuration

Defines URL patterns for analytics views and API endpoints.
Integrates with:
- DRF router
- Admin views
- API authentication
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsAPIView,
    AnalyticsDashboardView,
    ReportDownloadView
)

router = DefaultRouter()

app_name = 'analytics'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', AnalyticsAPIView.as_view(), name='stats'),
    path('api/reports/download/', ReportDownloadView.as_view(), name='download-report'),
    
    # Dashboard views
    path('dashboard/', AnalyticsDashboardView.as_view(), name='dashboard'),
]
