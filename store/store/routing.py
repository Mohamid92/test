from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from analytics.consumers import AnalyticsConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/analytics/$', AnalyticsConsumer.as_asgi()),
        ])
    ),
})
