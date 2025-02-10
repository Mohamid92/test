"""
Analytics Tasks

Celery tasks for analytics processing and reporting.
Integrates with:
- Email notifications
- Data aggregation
- Report generation
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import PageView, ProductView, CartAbandonment
from .reports import (
    DailyAnalyticsReport,
    WeeklyAnalyticsReport,
    MonthlyAnalyticsReport
)
from datetime import datetime, timedelta

@shared_task
def calculate_daily_analytics():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Get yesterday's payment logs
    logs = PaymentLog.objects.filter(created_at__date=yesterday)
    
    analytics, _ = PaymentAnalytics.objects.get_or_create(date=yesterday)
    analytics.total_transactions = logs.count()
    analytics.successful_transactions = logs.filter(status='SUCCESS').count()
    analytics.failed_transactions = logs.filter(status='FAILED').count()
    analytics.total_amount = logs.filter(status='SUCCESS').aggregate(
        total=Sum('amount'))['total'] or 0
    analytics.refund_amount = logs.filter(status='REFUNDED').aggregate(
        total=Sum('amount'))['total'] or 0
    analytics.save()

@shared_task
def send_daily_report():
    config = StoreConfiguration.objects.first()
    if config and config.enable_order_emails:
        return ReportGenerator.send_daily_report_email(config)
    return False

@shared_task
def send_weekly_report():
    config = StoreConfiguration.objects.first()
    if not config or not config.enable_order_emails:
        return False
        
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    csv_content = ReportGenerator.generate_csv_report(start_date, end_date)
    
    email = EmailMessage(
        subject=f'Weekly Payment Report ({start_date} to {end_date})',
        body='Please find attached the weekly payment report.',
        from_email=config.from_email,
        to=[config.admin_email]
    )
    
    email.attach(f'weekly_report_{end_date}.csv', csv_content, 'text/csv')
    return email.send()

@shared_task
def generate_monthly_report():
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_month = first_day - timedelta(days=1)
    start_date = last_month.replace(day=1)
    
    config = StoreConfiguration.objects.first()
    if not config or not config.enable_order_emails:
        return False
        
    # Generate Excel report
    generator = ExcelReportGenerator(start_date, last_month)
    excel_file = generator.generate_report()
    
    # Generate PDF report
    pdf_generator = PaymentReportGenerator(start_date, last_month)
    pdf_file = pdf_generator.generate_report()
    
    # Send email with both reports
    email = EmailMessage(
        subject=f'Monthly Payment Report - {last_month.strftime("%B %Y")}',
        body='Please find attached the monthly payment reports.',
        from_email=config.from_email,
        to=[config.admin_email]
    )
    
    email.attach(f'monthly_report_{last_month.strftime("%Y_%m")}.xlsx', 
                excel_file.getvalue(),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    email.attach(f'monthly_report_{last_month.strftime("%Y_%m")}.pdf',
                pdf_file.getvalue(),
                'application/pdf')
    
    return email.send()

@shared_task
def process_cart_abandonments():
    """
    Process abandoned carts and trigger recovery actions.
    Called by:
    - Celery beat scheduler
    - Manual admin trigger
    """
    threshold = timezone.now() - timedelta(hours=1)
    abandonments = CartAbandonment.objects.filter(
        abandoned_at__lte=threshold,
        recovered=False
    )
    
    for abandonment in abandonments:
        try:
            # Trigger recovery workflow
            if abandonment.user and abandonment.user.email:
                send_cart_recovery_email.delay(abandonment.id)
            
            # Track for analytics
            log_cart_abandonment.delay(abandonment.id)
        except Exception as e:
            print(f"Error processing abandonment {abandonment.id}: {str(e)}")

@shared_task
def aggregate_daily_analytics():
    """
    Aggregates daily analytics metrics
    Scheduled: Daily at midnight
    """
    yesterday = datetime.now().date() - timedelta(days=1)
    report = DailyAnalyticsReport(yesterday)
    report.generate()
    send_daily_report.delay(yesterday)

@shared_task
def clean_old_analytics():
    """
    Cleans up old analytics data
    Retention: 90 days for detailed data
    """
    cutoff_date = datetime.now() - timedelta(days=90)
    PageView.objects.filter(created_at__lt=cutoff_date).delete()
    ProductView.objects.filter(viewed_at__lt=cutoff_date).delete()

# ... Additional analytics tasks ...
