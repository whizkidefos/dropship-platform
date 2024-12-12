from flask import Blueprint, render_template, request, jsonify
from app.models.product import Product
from sqlalchemy import desc
from app import db

products = Blueprint('products', __name__)

@products.route('/catalog')
def catalog():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Products per page
    
    # Get filter parameters
    category = request.args.get('category')
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search')
    
    # Base query
    query = Product.query.filter_by(is_active=True)
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.title.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:  # newest
        query = query.order_by(desc(Product.created_at))
    
    # Get categories for filter sidebar
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Paginate results
    products = query.paginate(page=page, per_page=per_page)
    
    return render_template('products/catalog.html',
                         products=products,
                         categories=categories,
                         current_category=category,
                         current_sort=sort,
                         min_price=min_price,
                         max_price=max_price,
                         search=search)

@products.route('/<int:id>')
def detail(id):
    product = Product.query.get_or_404(id)
    
    # Get related products (same category)
    related_products = Product.query\
        .filter_by(category=product.category)\
        .filter(Product.id != id)\
        .filter_by(is_active=True)\
        .limit(4)\
        .all()
    
    return render_template('products/detail.html',
                         product=product,
                         related_products=related_products)

@products.route('/api/quick-view/<int:id>')
def quick_view(id):
    """API endpoint for quick view modal"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'title': product.title,
        'price': float(product.price),
        'description': product.description,
        'main_image': product.images[0].url if product.images else None,
        'stock_level': product.stock_level,
        'detail_url': url_for('products.detail', id=product.id)
    })