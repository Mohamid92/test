from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('api/analytics/', views.AnalyticsAPIView.as_view(), name='analytics-data'),
    path('api/analytics/payments/', views.PaymentReconciliationView.as_view(), name='payment-reconciliation'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/sales-report/', views.SalesReportView.as_view(), name='sales-report'),
    path('dashboard/payment-methods/', views.PaymentMethodsView.as_view(), name='payment-methods'),
    path('dashboard/export/<str:report_type>/', views.ExportReportView.as_view(), name='export-report'),
]
