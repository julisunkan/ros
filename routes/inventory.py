from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Product, Category, SaleItem
from forms import ProductForm, CategoryForm
from app import db
from sqlalchemy import func, desc
from utils import generate_barcode

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

def check_permission(required_roles):
    if not current_user.can_access(required_roles):
        flash('You do not have permission to access this page', 'error')
        return False
    return True

@bp.route('/products')
@login_required
def products():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', '')
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.order_by(Product.name).all()
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('inventory/products.html', 
                         products=products, 
                         categories=categories,
                         search=search,
                         category_id=category_id)

@bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('inventory.products'))
    
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            barcode=form.barcode.data,
            price=form.price.data,
            cost=form.cost.data,
            stock_quantity=form.stock_quantity.data,
            low_stock_threshold=form.low_stock_threshold.data,
            category_id=form.category_id.data,
            is_active=form.is_active.data
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('inventory.products'))
    
    return render_template('inventory/add_product.html', form=form)

@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('inventory.products'))
    
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.barcode = form.barcode.data
        product.price = form.price.data
        product.cost = form.cost.data
        product.stock_quantity = form.stock_quantity.data
        product.low_stock_threshold = form.low_stock_threshold.data
        product.category_id = form.category_id.data
        product.is_active = form.is_active.data
        
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('inventory.products'))
    
    return render_template('inventory/edit_product.html', form=form, product=product)

@bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('inventory.products'))
    
    product = Product.query.get_or_404(product_id)
    
    # Check if product has sales history
    if SaleItem.query.filter_by(product_id=product_id).first():
        product.is_active = False
        flash('Product deactivated (has sales history)', 'warning')
    else:
        db.session.delete(product)
        flash('Product deleted successfully', 'success')
    
    db.session.commit()
    return redirect(url_for('inventory.products'))

@bp.route('/categories')
@login_required
def categories():
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('main.dashboard'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('inventory/categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('inventory.categories'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully', 'success')
        return redirect(url_for('inventory.categories'))
    
    return render_template('inventory/add_category.html', form=form)

@bp.route('/api/products/search')
@login_required
def search_products():
    """API endpoint for product search (used in POS)"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.contains(query),
        Product.is_active == True,
        Product.stock_quantity > 0
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'stock': p.stock_quantity,
        'barcode': p.barcode
    } for p in products])

@bp.route('/api/products/<barcode>')
@login_required
def get_product_by_barcode(barcode):
    """API endpoint to get product by barcode"""
    product = Product.query.filter_by(barcode=barcode, is_active=True).first()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.stock_quantity <= 0:
        return jsonify({'error': 'Product out of stock'}), 400
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'stock': product.stock_quantity,
        'barcode': product.barcode
    })
