from app import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)  # Supplier's price
    markup_percentage = db.Column(db.Float, default=20.0)  # Default 20% markup
    stock_level = db.Column(db.Integer, default=0)
    vendor_url = db.Column(db.String(500))  # Original product URL
    vendor_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')

    def calculate_profit_margin(self):
        """Calculate profit margin percentage"""
        if self.price and self.cost:
            return ((self.price - self.cost) / self.price) * 100
        return 0

    def update_price_from_markup(self):
        """Update selling price based on cost and markup percentage"""
        if self.cost and self.markup_percentage:
            markup_multiplier = 1 + (self.markup_percentage / 100)
            self.price = round(self.cost * markup_multiplier, 2)

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductImage {self.id} for Product {self.product_id}>'