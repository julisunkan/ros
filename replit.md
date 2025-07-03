# POS System - Replit Configuration

## Overview

This is a comprehensive Point of Sale (POS) system built with Flask, featuring inventory management, sales processing, customer management, and reporting capabilities. The system is designed for retail environments with role-based access control and real-time inventory tracking.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF for form handling and validation
- **Templates**: Jinja2 templating engine
- **Middleware**: ProxyFix for proper handling of proxy headers

### Frontend Architecture
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JavaScript with Chart.js for data visualization
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Database Schema
The application uses SQLAlchemy with the following key models:
- **User**: Authentication and role management
- **Role**: Role-based access control (admin, manager, cashier)
- **Product**: Inventory items with stock tracking
- **Category**: Product categorization
- **Customer**: Customer information and loyalty points
- **Sale**: Transaction records
- **SaleItem**: Individual items within transactions

## Key Components

### Authentication System
- Login/logout functionality with Flask-Login
- Role-based access control with three levels: admin, manager, cashier
- Session management with secure secret key configuration
- User management interface for administrators

### Inventory Management
- Product catalog with categories, pricing, and stock levels
- Barcode support for product identification
- Low stock threshold alerts
- Category-based product organization
- Stock quantity tracking with automatic updates

### Point of Sale Interface
- Real-time product search and barcode scanning
- Shopping cart functionality with session storage
- Multiple payment methods (cash, card, etc.)
- Receipt generation and printing
- Customer selection and loyalty point tracking

### Reporting System
- Sales reports with date range filtering
- Inventory reports with stock level analysis
- Dashboard with key performance indicators
- Export functionality for CSV data
- Chart visualization for sales trends

### Customer Management
- Customer database with contact information
- Loyalty points system
- Purchase history tracking
- Customer search and filtering

## Data Flow

1. **User Authentication**: Users log in through the auth blueprint, establishing a session
2. **Product Management**: Administrators manage products through the inventory blueprint
3. **Sales Processing**: Cashiers process sales through the POS interface, updating inventory
4. **Receipt Generation**: Completed sales generate receipts and update customer records
5. **Reporting**: Managers access reports through the reports blueprint for business insights

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: Authentication management
- Flask-WTF: Form handling
- WTForms: Form validation
- ReportLab: PDF generation for receipts
- Python-barcode: Barcode generation
- Werkzeug: WSGI utilities and security

### Frontend Dependencies
- Bootstrap 5: UI framework (CDN)
- Bootstrap Icons: Icon library (CDN)
- Chart.js: Data visualization (CDN)

### Database Support
- SQLite: Local database for development and production (instance/pos.db)
- Configured to use local SQLite database instead of PostgreSQL per user preference

## Deployment Strategy

### Environment Configuration
- **SESSION_SECRET**: Secret key for session management
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **SQLALCHEMY_ENGINE_OPTIONS**: Database connection pooling configuration

### Application Structure
- **Main Entry Point**: `main.py` starts the Flask development server
- **Application Factory**: `app.py` configures the Flask application and extensions
- **Blueprint Organization**: Routes are organized by functionality (auth, inventory, sales, etc.)
- **Static Assets**: CSS and JavaScript files in the static directory
- **Templates**: Jinja2 templates organized by blueprint

### Production Considerations
- ProxyFix middleware for proper header handling behind proxies
- Database connection pooling with automatic reconnection
- Environment-based configuration for secrets and database URLs
- Debug mode disabled in production environments

## Changelog

- July 03, 2025. Initial setup
- July 03, 2025. Configured to use local SQLite database instead of PostgreSQL per user preference

## User Preferences

Preferred communication style: Simple, everyday language.
Database preference: Local SQLite database for development and production