from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import PageView, PaymentLog
from django.db.models import Sum

class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("analytics", self.channel_name)
        await self.accept()
        
        # Send initial stats
        stats = await self.get_current_stats()
        await self.send(json.dumps(stats))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("analytics", self.channel_name)

    async def receive(self, text_data):
        pass  # We don't expect to receive messages

    async def analytics_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_current_stats(self):
        today = timezone.now().date()
        return {
            'active_users': PageView.objects.filter(
                created_at__date=today
            ).values('session_id').distinct().count(),
            'page_views': PageView.objects.filter(
                created_at__date=today
            ).count(),
            'sales': PaymentLog.objects.filter(
                created_at__date=today,
                status='SUCCESS'
            ).count(),
            'revenue': float(PaymentLog.objects.filter(
                created_at__date=today,
                status='SUCCESS'
            ).aggregate(total=Sum('amount'))['total'] or 0)
        }
