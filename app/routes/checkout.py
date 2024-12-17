from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app import db
import stripe
import json

checkout = Blueprint('checkout', __name__)

@checkout.route('/checkout', methods=['GET'])
@login_required
def checkout_start():
    cart = Cart(session)
    if len(cart) == 0:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    return render_template('checkout/index.html', cart=cart)

@checkout.route('/checkout/shipping', methods=['GET', 'POST'])
@login_required
def shipping():
    cart = Cart(session)
    if len(cart) == 0:
        return redirect(url_for('cart.view_cart'))
    
    if request.method == 'POST':
        shipping_data = {
            'full_name': request.form.get('full_name'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country'),
            'phone': request.form.get('phone')
        }
        
        session['checkout_shipping'] = shipping_data
        return redirect(url_for('checkout.payment'))
    
    return render_template('checkout/shipping.html', 
                         cart=cart,
                         shipping_info=session.get('checkout_shipping', {}))

@checkout.route('/checkout/payment', methods=['GET', 'POST'])
@login_required
def payment():
    cart = Cart(session)
    if len(cart) == 0:
        return redirect(url_for('cart.view_cart'))
    
    if 'checkout_shipping' not in session:
        return redirect(url_for('checkout.shipping'))
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    intent = stripe.PaymentIntent.create(
        amount=int(cart.cart['total_amount'] * 100),  # Amount in cents
        currency='usd',
        metadata={'user_id': current_user.id}
    )
    
    return render_template('checkout/payment.html',
                         cart=cart,
                         client_secret=intent.client_secret,
                         stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'])

@checkout.route('/checkout/process', methods=['POST'])
@login_required
def process_order():
    cart = Cart(session)
    if len(cart) == 0:
        return jsonify({'error': 'Empty cart'}), 400
    
    try:
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=cart.cart['total_amount'],
            shipping_address=session['checkout_shipping'],
            payment_method='stripe',
            status='pending'
        )
        
        # Add order items
        for item in cart:
            order_item = OrderItem(
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            order.items.append(order_item)
        
        db.session.add(order)
        db.session.commit()
        
        # Clear cart and checkout data
        cart.clear()
        session.pop('checkout_shipping', None)
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'redirect_url': url_for('checkout.confirmation', order_id=order.id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@checkout.route('/checkout/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    return render_template('checkout/confirmation.html', order=order)