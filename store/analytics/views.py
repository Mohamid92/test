from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from rest_framework import status
from orders.models import PaymentLog, PaymentAnalytics
from store.analytics.reports import ExcelReportGenerator, PaymentReportGenerator, ReportGenerator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta

class AnalyticsAPIView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        analytics = PaymentAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')

        data = {
            'dates': [],
            'successful_transactions': [],
            'failed_transactions': [],
            'revenue': [],
            'payment_methods': {}
        }

        for entry in analytics:
            data['dates'].append(entry.date.strftime('%Y-%m-%d'))
            data['successful_transactions'].append(entry.successful_transactions)
            data['failed_transactions'].append(entry.failed_transactions)
            data['revenue'].append(float(entry.total_amount))

        # Get payment method distribution
        payment_methods = PaymentLog.objects.filter(
            created_at__date__range=[start_date, end_date],
            status='SUCCESS'
        ).values('gateway').annotate(
            total=Count('id')
        )

        for method in payment_methods:
            data['payment_methods'][method['gateway']] = method['total']

        return Response(data)

class GenerateReportView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Please provide start_date and end_date'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            generator = PaymentReportGenerator(start_date, end_date)
            buffer = generator.generate_report()
            buffer.seek(0)
            
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=payment_report_{start_date}_{end_date}.pdf'
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        report_type = request.data.get('type', 'csv')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Please provide start_date and end_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            if report_type == 'excel':
                generator = ExcelReportGenerator(start_date, end_date)
                excel_file = generator.generate_report()
                response = HttpResponse(
                    excel_file.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename=payment_report_{start_date}_{end_date}.xlsx'
                return response
            elif report_type == 'csv':
                content = ReportGenerator.generate_csv_report(start_date, end_date)
                response = HttpResponse(content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename=payment_report_{start_date}_{end_date}.csv'
                return response
            else:
                return Response(
                    {'error': 'Unsupported report type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Get last 30 days analytics
        context['analytics'] = PaymentAnalytics.objects.filter(
            date__gte=today - timedelta(days=30)
        ).order_by('date')
        
        # Calculate totals
        context['total_revenue'] = sum(a.total_amount for a in context['analytics'])
        context['total_transactions'] = sum(a.total_transactions for a in context['analytics'])
        context['success_rate'] = (
            sum(a.successful_transactions for a in context['analytics']) / 
            context['total_transactions'] * 100 if context['total_transactions'] > 0 else 0
        )
        
        return context

class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date = self.request.GET.get('start_date', 
            (timezone.now() - timedelta(days=30)).date().isoformat()
        )
        end_date = self.request.GET.get('end_date', 
            timezone.now().date().isoformat()
        )
        
        # Get sales data
        context['sales_data'] = self.get_sales_data(start_date, end_date)
        return context
    
    def get_sales_data(self, start_date, end_date):
        return PaymentLog.objects.filter(
            status='SUCCESS',
            created_at__date__range=[start_date, end_date]
        ).values('created_at__date').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('created_at__date')
