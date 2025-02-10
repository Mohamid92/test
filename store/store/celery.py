from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')

app = Celery('store')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'calculate-daily-analytics': {
        'task': 'analytics.tasks.calculate_daily_analytics',
        'schedule': crontab(hour=0, minute=5),  # Run at 00:05 every day
    },
}

app.conf.beat_schedule.update({
    'daily-payment-report': {
        'task': 'analytics.tasks.send_daily_report',
        'schedule': crontab(hour=1, minute=0),  # Run at 1 AM
    },
    'weekly-payment-report': {
        'task': 'analytics.tasks.send_weekly_report',
        'schedule': crontab(day_of_week='monday', hour=2, minute=0),  # Run at 2 AM on Mondays
    },
    'monthly-payment-report': {
        'task': 'analytics.tasks.generate_monthly_report',
        'schedule': crontab(day_of_month='1', hour=3, minute=0),  # Run at 3 AM on first day of month
    }
})
