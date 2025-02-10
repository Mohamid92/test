"""
Analytics Middleware

Processes requests/responses for analytics tracking.
Integrates with session management and user tracking.
"""

from django.utils.deprecation import MiddlewareMixin
import time
from .tracking import UserTracker

class AnalyticsMiddleware(MiddlewareMixin):
    """
    Core analytics middleware
    
    Tracks:
    - Page views
    - Response times
    - User sessions
    - Device info
    """
    
    def process_request(self, request):
        """Initialize analytics tracking for request"""
        request.analytics_start_time = time.time()
        request.tracker = UserTracker(request)
        
        # Skip analytics for admin/static/media
        if not self.should_track_request(request.path):
            return
            
        request.tracker.track_page_view()

    def process_response(self, request, response):
        """Process response for analytics"""
        if hasattr(request, 'analytics_start_time'):
            duration = time.time() - request.analytics_start_time
            
            if hasattr(request, 'tracker'):
                request.tracker.track_response_time(duration)
        
        return response

    @staticmethod
    def should_track_request(path):
        """Determine if request should be tracked"""
        excluded_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/__debug__/',
            '/favicon.ico'
        ]
        return not any(path.startswith(prefix) for prefix in excluded_paths)
