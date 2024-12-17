from app import db
from datetime import datetime

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
    return f'ORD-{timestamp}-{uuid.uuid4().hex[:8].upper()}'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, default=generate_order_number)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, processing, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    
    # Shipping Information
    shipping_address = db.Column(db.JSON, nullable=False)
    shipping_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    
    # Payment Information
    payment_status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True)
    

    def generate_order_number(self):
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        return f'ORD-{timestamp}-{self.id:04d}'

    def calculate_total(self):
        """Calculate total order amount"""
        return sum(item.subtotal for item in self.items)

    @property
    def status_display(self):
        """Get status display text"""
        return self.status.title()

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')

    @property
    def subtotal(self):
        """Calculate subtotal for item"""
        return self.quantity * self.price

class OrderLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='logs')