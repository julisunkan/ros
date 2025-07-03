from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Role, Settings, Category
from forms import UserForm, SettingsForm, CategoryForm
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin():
    if not current_user.has_role('admin'):
        flash('Admin access required', 'error')
        return False
    return True

@bp.route('/')
@login_required
def admin_dashboard():
    if not check_admin():
        return redirect(url_for('main.dashboard'))
    
    # Get system statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users)

@bp.route('/users')
@login_required
def users():
    if not check_admin():
        return redirect(url_for('main.dashboard'))
    
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not check_admin():
        return redirect(url_for('admin.users'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role_id=form.role_id.data,
            is_active=form.is_active.data
        )
        
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', form=form)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not check_admin():
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # Don't require password for editing
    form.password.validators = []
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role_id.data
        user.is_active = form.is_active.data
        
        # Only update password if provided
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not check_admin():
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deletion of current user
    if user.id == current_user.id:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not check_admin():
        return redirect(url_for('main.dashboard'))
    
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    
    form = SettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.store_name = form.store_name.data
        settings.store_address = form.store_address.data
        settings.store_phone = form.store_phone.data
        settings.store_email = form.store_email.data
        settings.tax_rate = form.tax_rate.data
        settings.currency = form.currency.data
        settings.receipt_footer = form.receipt_footer.data
        settings.low_stock_alerts = form.low_stock_alerts.data
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)

@bp.route('/categories')
@login_required
def categories():
    if not check_admin():
        return redirect(url_for('main.dashboard'))
    
    from flask_wtf import FlaskForm
    form = FlaskForm()  # Create form for CSRF token
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories, form=form)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not check_admin():
        return redirect(url_for('admin.categories'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/add_category.html', form=form)

@bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if not check_admin():
        return redirect(url_for('admin.categories'))
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/edit_category.html', form=form, category=category)

@bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if not check_admin():
        return redirect(url_for('admin.categories'))
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    if category.products:
        flash('Cannot delete category with existing products', 'error')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('admin.categories'))
