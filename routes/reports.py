from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from models import Sale, Product, Customer, SaleItem
from app import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from utils import export_to_csv
import json

bp = Blueprint('reports', __name__, url_prefix='/reports')

def check_permission(required_roles):
    if not current_user.can_access(required_roles):
        return False
    return True

@bp.route('/sales')
@login_required
def sales_report():
    if not check_permission(['admin', 'manager']):
        return render_template('error.html', message='Access denied')
    
    # Get date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Build query
    query = Sale.query.filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date
    )
    
    # Get sales data
    sales = query.order_by(desc(Sale.created_at)).all()
    
    # Calculate summary statistics
    total_sales = len(sales)
    total_revenue = sum(sale.total_amount for sale in sales)
    avg_sale = total_revenue / total_sales if total_sales > 0 else 0
    
    # Daily sales data for chart
    daily_sales = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.count(Sale.id).label('count'),
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date
    ).group_by(func.date(Sale.created_at)).all()
    
    # Payment method breakdown
    payment_methods = db.session.query(
        Sale.payment_method,
        func.count(Sale.id).label('count'),
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date
    ).group_by(Sale.payment_method).all()
    
    # Top selling products
    top_products = db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label('quantity_sold'),
        func.sum(SaleItem.total_price).label('revenue')
    ).join(SaleItem).join(Sale).filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date
    ).group_by(Product.id, Product.name).order_by(desc('quantity_sold')).limit(10).all()
    
    # Prepare chart data
    chart_data = {
        'daily_sales': [{'date': str(d.date), 'count': d.count, 'revenue': float(d.revenue)} for d in daily_sales],
        'payment_methods': [{'method': p.payment_method, 'count': p.count, 'revenue': float(p.revenue)} for p in payment_methods],
        'top_products': [{'name': p.name, 'quantity': p.quantity_sold, 'revenue': float(p.revenue)} for p in top_products]
    }
    
    return render_template('reports/sales_report.html',
                         sales=sales,
                         total_sales=total_sales,
                         total_revenue=total_revenue,
                         avg_sale=avg_sale,
                         daily_sales=daily_sales,
                         payment_methods=payment_methods,
                         top_products=top_products,
                         chart_data=json.dumps(chart_data),
                         start_date=start_date,
                         end_date=end_date)

@bp.route('/inventory')
@login_required
def inventory_report():
    if not check_permission(['admin', 'manager']):
        return render_template('error.html', message='Access denied')
    
    # Get all products with stock information
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    # Calculate inventory value
    total_value = sum(product.price * product.stock_quantity for product in products)
    total_cost = sum(product.cost * product.stock_quantity for product in products)
    
    # Low stock items
    low_stock_items = [p for p in products if p.is_low_stock]
    
    # Out of stock items
    out_of_stock_items = [p for p in products if p.stock_quantity == 0]
    
    return render_template('reports/inventory_report.html',
                         products=products,
                         total_value=total_value,
                         total_cost=total_cost,
                         low_stock_items=low_stock_items,
                         out_of_stock_items=out_of_stock_items)

@bp.route('/export/sales')
@login_required
def export_sales():
    if not check_permission(['admin', 'manager']):
        return render_template('error.html', message='Access denied')
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get sales data
    sales = Sale.query.filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date
    ).order_by(desc(Sale.created_at)).all()
    
    # Prepare data for CSV
    headers = ['Sale Number', 'Date', 'Customer', 'Cashier', 'Subtotal', 'Tax', 'Discount', 'Total', 'Payment Method']
    data = []
    
    for sale in sales:
        data.append([
            sale.sale_number,
            sale.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sale.customer.name if sale.customer else 'Walk-in',
            sale.cashier.username,
            str(sale.subtotal),
            str(sale.tax_amount),
            str(sale.discount_amount),
            str(sale.total_amount),
            sale.payment_method
        ])
    
    csv_data = export_to_csv(data, headers)
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{start_date}_to_{end_date}.csv'
    
    return response

@bp.route('/export/inventory')
@login_required
def export_inventory():
    if not check_permission(['admin', 'manager']):
        return render_template('error.html', message='Access denied')
    
    # Get products data
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    # Prepare data for CSV
    headers = ['Product Name', 'Category', 'Price', 'Cost', 'Stock Quantity', 'Low Stock Threshold', 'Status']
    data = []
    
    for product in products:
        status = 'Out of Stock' if product.stock_quantity == 0 else 'Low Stock' if product.is_low_stock else 'In Stock'
        data.append([
            product.name,
            product.category.name if product.category else 'No Category',
            str(product.price),
            str(product.cost),
            str(product.stock_quantity),
            str(product.low_stock_threshold),
            status
        ])
    
    csv_data = export_to_csv(data, headers)
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=inventory_report.csv'
    
    return response
