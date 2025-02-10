from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum
from orders.models import PaymentLog, PaymentAnalytics
import io
import csv
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import xlsxwriter
from io import BytesIO

class PaymentReportGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()

    def generate_report(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        elements = []
        elements.extend(self._create_header())
        elements.extend(self._create_summary_table())
        elements.extend(self._create_gateway_breakdown())
        elements.extend(self._create_daily_breakdown())

        doc.build(elements)
        return self.buffer

    def _create_header(self):
        title = Paragraph(
            f"Payment Report ({self.start_date} to {self.end_date})",
            self.styles['Heading1']
        )
        return [title, Spacer(1, 20)]

    def _create_summary_table(self):
        analytics = PaymentAnalytics.objects.filter(
            date__range=[self.start_date, self.end_date]
        ).aggregate(
            total_trans=Sum('total_transactions'),
            successful_trans=Sum('successful_transactions'),
            total_amount=Sum('total_amount'),
            refund_amount=Sum('refund_amount')
        )

        data = [
            ['Metric', 'Value'],
            ['Total Transactions', analytics['total_trans'] or 0],
            ['Successful Transactions', analytics['successful_trans'] or 0],
            ['Total Revenue', f"QAR {analytics['total_amount'] or 0:,.2f}"],
            ['Total Refunds', f"QAR {analytics['refund_amount'] or 0:,.2f}"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        return [table, Spacer(1, 20)]

class ReportGenerator:
    @staticmethod
    def generate_csv_report(start_date, end_date):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Date', 'Total Transactions', 'Successful', 'Failed', 'Total Amount', 'Refunds'])
        
        analytics = PaymentAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        for entry in analytics:
            writer.writerow([
                entry.date,
                entry.total_transactions,
                entry.successful_transactions,
                entry.failed_transactions,
                entry.total_amount,
                entry.refund_amount
            ])
        
        return buffer.getvalue()

    @staticmethod
    def send_daily_report_email(config, report_date=None):
        if not report_date:
            report_date = datetime.now().date() - timedelta(days=1)
            
        analytics = PaymentAnalytics.objects.filter(date=report_date).first()
        if not analytics:
            return False
            
        context = {
            'analytics': analytics,
            'date': report_date,
            'success_rate': round(
                (analytics.successful_transactions / analytics.total_transactions * 100)
                if analytics.total_transactions > 0 else 0,
                2
            )
        }
        
        html_content = render_to_string('analytics/email/daily_report.html', context)
        
        email = EmailMessage(
            subject=f'Daily Payment Report - {report_date}',
            body=html_content,
            from_email=config.from_email,
            to=[config.admin_email]
        )
        email.content_subtype = "html"
        
        # Attach CSV
        csv_content = ReportGenerator.generate_csv_report(report_date, report_date)
        email.attach(f'payment_report_{report_date}.csv', csv_content, 'text/csv')
        
        return email.send()

class ExcelReportGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.output = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output)
        
    def generate_report(self):
        self._create_summary_sheet()
        self._create_daily_breakdown_sheet()
        self._create_gateway_analysis_sheet()
        self.workbook.close()
        self.output.seek(0)
        return self.output

    def _create_summary_sheet(self):
        worksheet = self.workbook.add_worksheet('Summary')
        bold = self.workbook.add_format({'bold': True})
        money = self.workbook.add_format({'num_format': 'QAR #,##0.00'})
        
        analytics = PaymentAnalytics.objects.filter(
            date__range=[self.start_date, self.end_date]
        ).aggregate(
            total_amount=Sum('total_amount'),
            total_trans=Sum('total_transactions'),
            success_trans=Sum('successful_transactions')
        )
        
        data = [
            ['Period', f"{self.start_date} to {self.end_date}"],
            ['Total Revenue', analytics['total_amount'] or 0],
            ['Total Transactions', analytics['total_trans'] or 0],
            ['Success Rate', f"{(analytics['success_trans'] or 0) / (analytics['total_trans'] or 1) * 100:.2f}%"]
        ]
        
        for row, (label, value) in enumerate(data):
            worksheet.write(row, 0, label, bold)
            worksheet.write(row, 1, value, money if 'Revenue' in label else None)

    def _create_daily_breakdown_sheet(self):
        worksheet = self.workbook.add_worksheet('Daily Breakdown')
        headers = ['Date', 'Transactions', 'Success', 'Failed', 'Revenue', 'Refunds']
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
            
        analytics = PaymentAnalytics.objects.filter(
            date__range=[self.start_date, self.end_date]
        ).order_by('date')
        
        for row, entry in enumerate(analytics, start=1):
            worksheet.write(row, 0, entry.date.strftime('%Y-%m-%d'))
            worksheet.write(row, 1, entry.total_transactions)
            worksheet.write(row, 2, entry.successful_transactions)
            worksheet.write(row, 3, entry.failed_transactions)
            worksheet.write(row, 4, float(entry.total_amount))
            worksheet.write(row, 5, float(entry.refund_amount))
