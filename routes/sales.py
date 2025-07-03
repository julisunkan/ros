from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import login_required, current_user
from models import Sale, SaleItem, Product, Customer, Settings
from forms import SaleForm
from app import db
from utils import generate_sale_number, calculate_tax, generate_receipt_pdf
from datetime import datetime, timezone
from sqlalchemy import desc

bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/')
@login_required
def sales():
    """POS Interface"""
    form = SaleForm()
    products = Product.query.filter_by(is_active=True).limit(20).all()
    
    # Get cart from session
    cart = session.get('cart', {})
    
    return render_template('pos/sales.html', form=form, products=products, cart=cart)

@bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to cart"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    
    if product.stock_quantity < quantity:
        flash('Insufficient stock', 'error')
        return redirect(url_for('sales.sales'))
    
    cart = session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity
        }
    
    session['cart'] = cart
    flash(f'Added {product.name} to cart', 'success')
    return redirect(url_for('sales.sales'))

@bp.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    """Update cart item quantity"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    
    cart = session.get('cart', {})
    
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] = quantity
    
    session['cart'] = cart
    return redirect(url_for('sales.sales'))

@bp.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove item from cart"""
    product_id = request.form.get('product_id')
    
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('sales.sales'))

@bp.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    """Clear entire cart"""
    session.pop('cart', None)
    flash('Cart cleared', 'success')
    return redirect(url_for('sales.sales'))

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Process sale checkout"""
    form = SaleForm()
    
    if not form.validate_on_submit():
        flash('Please fix form errors', 'error')
        return redirect(url_for('sales.sales'))
    
    cart = session.get('cart', {})
    
    if not cart:
        flash('Cart is empty', 'error')
        return redirect(url_for('sales.sales'))
    
    # Get settings for tax calculation
    settings = Settings.query.first()
    tax_rate = settings.tax_rate if settings else 0
    
    # Calculate totals with proper decimal handling
    from decimal import Decimal
    subtotal = sum(float(item['price']) * item['quantity'] for item in cart.values())
    discount_amount = float(form.discount_amount.data or 0)
    tax_amount = calculate_tax(subtotal - discount_amount, float(tax_rate) if tax_rate else 0)
    total_amount = subtotal - discount_amount + tax_amount
    
    # Create sale record
    sale = Sale(
        sale_number=generate_sale_number(),
        customer_id=form.customer_id.data if form.customer_id.data else None,
        user_id=current_user.id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        payment_method=form.payment_method.data,
        payment_status='completed',
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(sale)
    db.session.flush()  # Get the sale ID
    
    # Create sale items and update inventory
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        
        if product.stock_quantity < item['quantity']:
            db.session.rollback()
            flash(f'Insufficient stock for {product.name}', 'error')
            return redirect(url_for('sales.sales'))
        
        # Create sale item
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=int(product_id),
            quantity=item['quantity'],
            unit_price=float(item['price']),
            total_price=float(item['price']) * item['quantity']
        )
        db.session.add(sale_item)
        
        # Update product stock
        product.stock_quantity -= item['quantity']
    
    db.session.commit()
    
    # Clear cart
    session.pop('cart', None)
    
    flash('Sale completed successfully', 'success')
    return redirect(url_for('sales.receipt', sale_id=sale.id))

@bp.route('/receipt/<int:sale_id>')
@login_required
def receipt(sale_id):
    """Display receipt"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('receipts/receipt.html', sale=sale)

@bp.route('/receipt/<int:sale_id>/pdf')
@login_required
def receipt_pdf(sale_id):
    """Generate PDF receipt"""
    sale = Sale.query.get_or_404(sale_id)
    
    pdf_buffer = generate_receipt_pdf(sale)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{sale.sale_number}.pdf'
    
    return response

@bp.route('/history')
@login_required
def history():
    """Sales history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    sales = Sale.query.order_by(desc(Sale.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('sales/history.html', sales=sales)

@bp.route('/api/cart')
@login_required
def get_cart():
    """Get cart contents via API"""
    cart = session.get('cart', {})
    
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        item_total = item['price'] * item['quantity']
        cart_items.append({
            'product_id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })
        total += item_total
    
    return jsonify({
        'items': cart_items,
        'total': total,
        'count': len(cart_items)
    })
