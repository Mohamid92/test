from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from ..models import PageView, ProductView, UserBehavior, SearchQuery
import json

@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        # Add analytics data
        context.update({
            'page_views': self.get_page_views(start_date, end_date),
            'product_interactions': self.get_product_interactions(start_date, end_date),
            'search_analysis': self.get_search_analysis(start_date, end_date),
            'user_behavior': self.get_behavior_analysis(start_date, end_date)
        })
        
        return context

    def get_page_views(self, start_date, end_date):
        views = PageView.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('device_type').annotate(
            count=Count('id'),
            users=Count('user', distinct=True)
        )
        return list(views)

    def get_product_interactions(self, start_date, end_date):
        return ProductView.objects.filter(
            viewed_at__range=[start_date, end_date]
        ).values('product__name').annotate(
            views=Count('id'),
            avg_duration=Avg('duration')
        ).order_by('-views')[:10]

    def get_search_analysis(self, start_date, end_date):
        return SearchQuery.objects.filter(
            timestamp__range=[start_date, end_date]
        ).values('query').annotate(
            count=Count('id'),
            avg_results=Avg('results_count')
        ).order_by('-count')[:10]

    def get_behavior_analysis(self, start_date, end_date):
        return UserBehavior.objects.filter(
            timestamp__range=[start_date, end_date]
        ).values('behavior_type').annotate(
            count=Count('id')
        )
