import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database - using local SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pos.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default admin user if none exists
    from models import User, Role
    from werkzeug.security import generate_password_hash
    
    if not Role.query.first():
        # Create default roles
        admin_role = Role(name='admin', description='Administrator')
        manager_role = Role(name='manager', description='Manager')
        cashier_role = Role(name='cashier', description='Cashier')
        
        db.session.add_all([admin_role, manager_role, cashier_role])
        db.session.commit()
    
    if not User.query.first():
        # Create default admin user
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User(
            username='admin',
            email='admin@pos.com',
            password_hash=generate_password_hash('admin123'),
            role=admin_role,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Created default admin user: admin/admin123")

# Import routes
from routes import auth, main, inventory, customers, sales, reports, admin
app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.register_blueprint(inventory.bp)
app.register_blueprint(customers.bp)
app.register_blueprint(sales.bp)
app.register_blueprint(reports.bp)
app.register_blueprint(admin.bp)
