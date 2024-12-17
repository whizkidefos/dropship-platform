from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.cart import Cart
from app.models.product import Product
from flask_login import current_user

cart = Blueprint('cart', __name__)

@cart.route('/cart')
def view_cart():
    cart = Cart(session)
    return render_template('cart/cart.html', cart=cart)

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        cart = Cart(session)
        product = Product.query.get_or_404(product_id)
        quantity = int(request.form.get('quantity', 1))
        
        cart.add(product, quantity)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Product added to cart',
                'cart_total': len(cart),
                'cart_amount': cart.cart['total_amount']
            })
        
        return redirect(url_for('cart.view_cart'))
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@cart.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart():
    cart = Cart(session)
    quantity = int(request.form.get('quantity', 0))
    
    if quantity > 0:
        cart.update(product_id, quantity)
    else:
        cart.remove(product_id)
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'message': 'Cart updated',
            'cart_total': len(cart),
            'cart_amount': cart.cart['total_amount']
        })
        
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart():
    cart = Cart(session)
    cart.remove(product_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'message': 'Product removed from cart',
            'cart_total': len(cart),
            'cart_amount': cart.cart['total_amount']
        })
        
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/clear', methods=['POST'])
def clear_cart():
    cart = Cart(session)
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'message': 'Cart cleared',
            'cart_total': 0,
            'cart_amount': 0.00
        })
        
    return redirect(url_for('cart.view_cart'))