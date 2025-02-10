from .tracking import UserTracker
from django.utils.deprecation import MiddlewareMixin
import time

class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if not hasattr(request, 'start_time'):
            return response

        # Don't track static/media files
        if '/static/' in request.path or '/media/' in request.path:
            return response

        tracker = UserTracker(request)
        tracker.track_page_view(request.path)

        # Track product views
        if 'product-detail' in request.resolver_match.url_name:
            duration = int((time.time() - request.start_time) * 1000)  # in milliseconds
            product = request.resolver_match.kwargs.get('product')
            if product:
                tracker.track_product_view(product, duration)

        return response
