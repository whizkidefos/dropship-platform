from app import db
from datetime import datetime

class Cart:
    def __init__(self, session):
        self.session = session
        cart = session.get('cart')
        if not cart:
            cart = {'items': {}, 'total_amount': 0.00, 'total_items': 0}
            session['cart'] = cart
        self.cart = cart

    def add(self, product, quantity=1):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart['items']:
            self.cart['items'][product_id] = {
                'id': product.id,
                'title': product.title,
                'price': float(product.price),
                'quantity': 0,
                'image': product.images[0].url if product.images else None
            }
        
        self.cart['items'][product_id]['quantity'] += quantity
        self.update_totals()
        self.save()

    def update(self, product_id, quantity):
        """Update the quantity of a product."""
        if str(product_id) in self.cart['items'] and quantity > 0:
            self.cart['items'][str(product_id)]['quantity'] = quantity
            self.update_totals()
            self.save()

    def remove(self, product_id):
        """Remove a product from the cart."""
        if str(product_id) in self.cart['items']:
            del self.cart['items'][str(product_id)]
            self.update_totals()
            self.save()

    def clear(self):
        """Remove all items from the cart."""
        self.cart['items'] = {}
        self.update_totals()
        self.save()

    def update_totals(self):
        """Update cart totals."""
        self.cart['total_items'] = sum(item['quantity'] for item in self.cart['items'].values())
        self.cart['total_amount'] = sum(item['price'] * item['quantity'] 
                                      for item in self.cart['items'].values())

    def save(self):
        """Save cart to session."""
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        """Iterate over cart items."""
        for item in self.cart['items'].values():
            yield item

    def __len__(self):
        """Return total number of items in cart."""
        return self.cart['total_items']