"""
Analytics App Configuration

Sets up signal handlers and initializes analytics components.
"""

from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Analytics & Reporting'

    def ready(self):
        """
        Initialize analytics components:
        - Register signal handlers
        - Setup tracking middleware
        - Initialize reporting tasks
        """
        from . import signals
        from .tasks import schedule_daily_reports
        schedule_daily_reports()
