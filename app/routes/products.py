from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.product import Product, ProductImage
from app import db
from sqlalchemy import desc
import json

products = Blueprint('products', __name__)

@products.route('/products')
def list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    sort = request.args.get('sort', 'newest')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:  # newest
        query = query.order_by(desc(Product.created_at))
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Product.category).distinct().all()
    
    return render_template('products/list.html', 
                         products=products,
                         categories=categories,
                         current_category=category,
                         current_sort=sort)

@products.route('/products/<int:id>')
def detail(id):
    product = Product.query.get_or_404(id)
    related_products = Product.query.filter_by(category=product.category)\
                                  .filter(Product.id != id)\
                                  .limit(4).all()
    return render_template('products/detail.html', 
                         product=product,
                         related_products=related_products)

@products.route('/api/products/<int:id>/check-stock')
def check_stock(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'stock_level': product.stock_level,
        'is_available': product.stock_level > 0
    })

# Admin Routes
@products.route('/admin/products')
@login_required
def admin_list():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    products = Product.query.order_by(desc(Product.created_at)).all()
    return render_template('admin/products/list.html', products=products)

@products.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
def admin_create():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        product = Product(
            sku=request.form['sku'],
            title=request.form['title'],
            description=request.form['description'],
            cost=float(request.form['cost']),
            markup_percentage=float(request.form['markup_percentage']),
            category=request.form['category'],
            vendor_name=request.form['vendor_name'],
            vendor_url=request.form['vendor_url']
        )
        product.update_price_from_markup()
        
        # Handle image URLs
        image_urls = json.loads(request.form['image_urls'])
        for idx, url in enumerate(image_urls):
            image = ProductImage(
                url=url,
                is_primary=(idx == 0)  # First image is primary
            )
            product.images.append(image)
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('products.admin_list'))
    
    return render_template('admin/products/create.html')

@products.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit(id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.sku = request.form['sku']
        product.title = request.form['title']
        product.description = request.form['description']
        product.cost = float(request.form['cost'])
        product.markup_percentage = float(request.form['markup_percentage'])
        product.category = request.form['category']
        product.vendor_name = request.form['vendor_name']
        product.vendor_url = request.form['vendor_url']
        product.update_price_from_markup()
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.admin_list'))
    
    return render_template('admin/products/edit.html', product=product)