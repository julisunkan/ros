from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Customer, Sale
from forms import CustomerForm
from app import db
from sqlalchemy import desc

bp = Blueprint('customers', __name__, url_prefix='/customers')

def check_permission(required_roles):
    if not current_user.can_access(required_roles):
        flash('You do not have permission to access this page', 'error')
        return False
    return True

@bp.route('/')
@login_required
def customers():
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(Customer.name.contains(search))
    
    customers = query.order_by(Customer.name).all()
    
    return render_template('customers/customers.html', 
                         customers=customers, 
                         search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if not check_permission(['admin', 'manager', 'cashier']):
        return redirect(url_for('customers.customers'))
    
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            loyalty_points=form.loyalty_points.data
        )
        
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers.customers'))
    
    return render_template('customers/add_customer.html', form=form)

@bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    if not check_permission(['admin', 'manager', 'cashier']):
        return redirect(url_for('customers.customers'))
    
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.loyalty_points = form.loyalty_points.data
        
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers.customers'))
    
    return render_template('customers/edit_customer.html', form=form, customer=customer)

@bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    if not check_permission(['admin', 'manager']):
        return redirect(url_for('customers.customers'))
    
    customer = Customer.query.get_or_404(customer_id)
    
    # Check if customer has sales history
    if Sale.query.filter_by(customer_id=customer_id).first():
        flash('Cannot delete customer with sales history', 'error')
    else:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully', 'success')
    
    return redirect(url_for('customers.customers'))

@bp.route('/<int:customer_id>')
@login_required
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # Get customer's purchase history
    sales = Sale.query.filter_by(customer_id=customer_id).order_by(desc(Sale.created_at)).all()
    
    # Calculate customer stats
    total_purchases = len(sales)
    total_spent = sum(sale.total_amount for sale in sales)
    
    return render_template('customers/view_customer.html', 
                         customer=customer, 
                         sales=sales,
                         total_purchases=total_purchases,
                         total_spent=total_spent)
