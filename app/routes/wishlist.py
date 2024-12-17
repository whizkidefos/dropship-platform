from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.wishlist import WishlistItem
from app.models.product import Product
from app import db

wishlist = Blueprint('wishlist', __name__)

@wishlist.route('/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        wishlist_item = WishlistItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if wishlist_item:
            db.session.delete(wishlist_item)
            message = 'Product removed from wishlist'
            is_in_wishlist = False
        else:
            wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
            db.session.add(wishlist_item)
            message = 'Product added to wishlist'
            is_in_wishlist = True
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'is_in_wishlist': is_in_wishlist
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@wishlist.route('/')
@login_required
def view_wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id)\
                                     .order_by(WishlistItem.created_at.desc())\
                                     .all()
    return render_template('wishlist/index.html', wishlist_items=wishlist_items)