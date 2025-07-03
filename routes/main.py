from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import Product, Sale, Customer, SaleItem, Settings
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    # Get key metrics for dashboard
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Sales metrics
    today_sales = Sale.query.filter(func.date(Sale.created_at) == today).count()
    today_revenue = Sale.query.filter(func.date(Sale.created_at) == today).with_entities(func.sum(Sale.total_amount)).scalar() or 0
    
    week_sales = Sale.query.filter(func.date(Sale.created_at) >= week_ago).count()
    week_revenue = Sale.query.filter(func.date(Sale.created_at) >= week_ago).with_entities(func.sum(Sale.total_amount)).scalar() or 0
    
    month_sales = Sale.query.filter(func.date(Sale.created_at) >= month_ago).count()
    month_revenue = Sale.query.filter(func.date(Sale.created_at) >= month_ago).with_entities(func.sum(Sale.total_amount)).scalar() or 0
    
    # Inventory metrics
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.low_stock_threshold, Product.is_active == True).count()
    
    # Customer metrics
    total_customers = Customer.query.count()
    
    # Recent sales
    recent_sales = Sale.query.order_by(desc(Sale.created_at)).limit(10).all()
    
    # Low stock alerts
    low_stock_items = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.is_active == True
    ).limit(5).all()
    
    # Chart data for sales over time (last 7 days)
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_sales = Sale.query.filter(func.date(Sale.created_at) == date).with_entities(func.sum(Sale.total_amount)).scalar() or 0
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    sales_data.reverse()  # Show chronological order
    
    return render_template('dashboard.html',
                         current_date=today.strftime('%B %d, %Y'),
                         today_sales=today_sales,
                         today_revenue=today_revenue,
                         week_sales=week_sales,
                         week_revenue=week_revenue,
                         month_sales=month_sales,
                         month_revenue=month_revenue,
                         total_products=total_products,
                         low_stock_products=low_stock_products,
                         total_customers=total_customers,
                         recent_sales=recent_sales,
                         low_stock_items=low_stock_items,
                         sales_data=json.dumps(sales_data))
