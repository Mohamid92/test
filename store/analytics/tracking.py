from django.utils import timezone
from .models import PageView, ProductView, CartAbandonment, UserSession, UserBehavior, SearchQuery
from django.contrib.sessions.models import Session

class UserTracker:
    def __init__(self, request):
        self.request = request
        self.session_id = request.session.session_key
        self.user = request.user if request.user.is_authenticated else None

    def track_page_view(self, path):
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        referrer = self.request.META.get('HTTP_REFERER', '')
        
        PageView.objects.create(
            session_id=self.session_id,
            user=self.user,
            url=self.request.build_absolute_uri(),
            path=path,
            referrer=referrer,
            device_type=self._get_device_type(user_agent),
            browser=self._get_browser(user_agent)
        )

    def track_product_view(self, product, duration=None):
        ProductView.objects.create(
            session_id=self.session_id,
            user=self.user,
            product=product,
            duration=duration
        )

    def track_cart_abandonment(self, cart):
        CartAbandonment.objects.create(
            cart=cart,
            user=self.user,
            cart_value=cart.total,
            items_count=cart.items.count()
        )

    def track_user_behavior(self, behavior_type, data):
        session = UserSession.objects.get_or_create(
            session_id=self.session_id,
            defaults={'user': self.user}
        )[0]
        
        UserBehavior.objects.create(
            session=session,
            behavior_type=behavior_type,
            data=data,
            url=self.request.build_absolute_uri()
        )

    def track_search(self, query, results_count, category=None):
        session = UserSession.objects.get_or_create(
            session_id=self.session_id,
            defaults={'user': self.user}
        )[0]
        
        SearchQuery.objects.create(
            session=session,
            query=query,
            results_count=results_count,
            category=category
        )

    def update_session_info(self, device_info):
        session = UserSession.objects.get_or_create(
            session_id=self.session_id,
            defaults={
                'user': self.user,
                'device_info': device_info
            }
        )[0]
        return session

    @staticmethod
    def _get_device_type(user_agent):
        if 'Mobile' in user_agent:
            return 'mobile'
        elif 'Tablet' in user_agent:
            return 'tablet'
        return 'desktop'

    @staticmethod
    def _get_browser(user_agent):
        browsers = {
            'Chrome': 'chrome',
            'Firefox': 'firefox',
            'Safari': 'safari',
            'Edge': 'edge',
            'MSIE': 'ie'
        }
        for browser in browsers:
            if browser in user_agent:
                return browsers[browser]
        return 'other'
