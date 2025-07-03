from app import db
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import func

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def has_role(self, role_name):
        return self.role.name == role_name
    
    def can_access(self, required_roles):
        return self.role.name in required_roles

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    barcode = db.Column(db.String(50), unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2), default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    loyalty_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sales = db.relationship('Sale', backref='customer', lazy=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    cashier = db.relationship('User', backref='sales')
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='sale_items')

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(200), default='POS Store')
    store_address = db.Column(db.Text)
    store_phone = db.Column(db.String(20))
    store_email = db.Column(db.String(120))
    tax_rate = db.Column(db.Numeric(5, 2), default=0.0)
    currency = db.Column(db.String(10), default='USD')
    receipt_footer = db.Column(db.Text)
    low_stock_alerts = db.Column(db.Boolean, default=True)
