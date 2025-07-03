import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from flask import current_app
from models import Settings
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
import csv
import io

def generate_barcode(code, format_type='code128'):
    """Generate barcode image"""
    try:
        barcode_class = barcode.get_barcode_class(format_type)
        code_instance = barcode_class(code, writer=ImageWriter())
        buffer = BytesIO()
        code_instance.write(buffer)
        return buffer.getvalue()
    except Exception as e:
        current_app.logger.error(f"Error generating barcode: {e}")
        return None

def generate_receipt_pdf(sale):
    """Generate PDF receipt for a sale"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Get store settings
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph(settings.store_name, title_style))
    
    if settings.store_address:
        story.append(Paragraph(settings.store_address, styles['Normal']))
    if settings.store_phone:
        story.append(Paragraph(f"Phone: {settings.store_phone}", styles['Normal']))
    if settings.store_email:
        story.append(Paragraph(f"Email: {settings.store_email}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Sale info
    story.append(Paragraph(f"<b>Receipt #: {sale.sale_number}</b>", styles['Normal']))
    story.append(Paragraph(f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"Cashier: {sale.cashier.username}", styles['Normal']))
    if sale.customer:
        story.append(Paragraph(f"Customer: {sale.customer.name}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Items table
    table_data = [['Item', 'Qty', 'Price', 'Total']]
    for item in sale.items:
        table_data.append([
            item.product.name,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total_price:.2f}"
        ])
    
    table = Table(table_data, colWidths=[3*inch, 0.5*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    story.append(Spacer(1, 20))
    
    # Totals
    story.append(Paragraph(f"<b>Subtotal: ${sale.subtotal:.2f}</b>", styles['Normal']))
    if sale.discount_amount > 0:
        story.append(Paragraph(f"<b>Discount: -${sale.discount_amount:.2f}</b>", styles['Normal']))
    if sale.tax_amount > 0:
        story.append(Paragraph(f"<b>Tax: ${sale.tax_amount:.2f}</b>", styles['Normal']))
    story.append(Paragraph(f"<b>Total: ${sale.total_amount:.2f}</b>", styles['Heading2']))
    story.append(Paragraph(f"<b>Payment Method: {sale.payment_method.title()}</b>", styles['Normal']))
    
    if settings.receipt_footer:
        story.append(Spacer(1, 20))
        story.append(Paragraph(settings.receipt_footer, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_to_csv(data, headers):
    """Export data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    return output.getvalue()

def generate_sale_number():
    """Generate unique sale number"""
    now = datetime.now()
    return f"SALE-{now.strftime('%Y%m%d%H%M%S')}"

def calculate_tax(amount, tax_rate):
    """Calculate tax amount"""
    from decimal import Decimal
    # Convert to Decimal for precise calculations
    amount_decimal = Decimal(str(amount))
    tax_rate_decimal = Decimal(str(tax_rate))
    return float(amount_decimal * (tax_rate_decimal / 100))

def get_currency_symbol(currency_code):
    """Get currency symbol from currency code"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'NGN': '₦',  # Nigerian Naira
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
        'INR': '₹',
        'CNY': '¥',
        'KRW': '₩',
        'BRL': 'R$',
        'MXN': '$',
        'ZAR': 'R',
        'GHS': '₵',  # Ghana Cedi
        'KES': 'KSh', # Kenyan Shilling
        'UGX': 'USh', # Ugandan Shilling
        'TZS': 'TSh', # Tanzanian Shilling
    }
    return currency_symbols.get(currency_code, currency_code)

def format_currency(amount, currency_code='USD'):
    """Format amount as currency"""
    symbol = get_currency_symbol(currency_code)
    return f"{symbol}{amount:.2f}"
