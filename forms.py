from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from models import Role, Category, Product, Customer

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role_id = SelectField('Role', choices=[], validators=[DataRequired()])
    is_active = BooleanField('Active')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(r.id, r.name.title()) for r in Role.query.all()]

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    barcode = StringField('Barcode', validators=[Optional(), Length(max=50)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    cost = DecimalField('Cost', validators=[Optional(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    low_stock_threshold = IntegerField('Low Stock Threshold', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', choices=[], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')

class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address')
    loyalty_points = IntegerField('Loyalty Points', validators=[Optional(), NumberRange(min=0)], default=0)

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', choices=[], validators=[Optional()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('check', 'Check'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    discount_amount = DecimalField('Discount Amount', validators=[Optional(), NumberRange(min=0)], default=0)
    
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        customers = Customer.query.all()
        self.customer_id.choices = [('', 'Walk-in Customer')] + [(c.id, c.name) for c in customers]

class SettingsForm(FlaskForm):
    store_name = StringField('Store Name', validators=[DataRequired(), Length(max=200)])
    store_address = TextAreaField('Store Address')
    store_phone = StringField('Store Phone', validators=[Optional(), Length(max=20)])
    store_email = StringField('Store Email', validators=[Optional(), Email()])
    tax_rate = DecimalField('Tax Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0.0)
    currency = StringField('Currency', validators=[Optional(), Length(max=10)], default='USD')
    receipt_footer = TextAreaField('Receipt Footer')
    low_stock_alerts = BooleanField('Enable Low Stock Alerts', default=True)
