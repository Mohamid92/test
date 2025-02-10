from django.urls import path
from .webhooks import payment_webhook

urlpatterns = [
    path('', payment_webhook, name='payment-webhook'),
]
