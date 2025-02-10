from email.message import EmailMessage
from celery import shared_task
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Sum
from orders.models import PaymentLog, PaymentAnalytics, StoreConfiguration
from .reports import ExcelReportGenerator, PaymentReportGenerator, ReportGenerator

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
