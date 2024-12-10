from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.models.product import Product, ProductImage
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import desc
import json
import csv
import io
import pandas as pd
from datetime import datetime

admin = Blueprint('admin', __name__)

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/dashboard')
@admin_required
def dashboard():
    # Get summary statistics
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    
    # Get recent products
    recent_products = Product.query.order_by(desc(Product.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         active_products=active_products,
                         total_users=total_users,
                         recent_products=recent_products)

@admin.route('/admin/products')
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    query = Product.query.order_by(desc(Product.created_at))
    
    # Filter handling
    status = request.args.get('status')
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    products = query.paginate(page=page, per_page=10)
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    return render_template('admin/products/index.html', 
                         products=products,
                         categories=categories)
    

@admin.route('/admin/products/create', methods=['GET', 'POST'])
@admin_required
def create_product():
    if request.method == 'POST':
        try:
            product = Product(
                sku=request.form['sku'],
                title=request.form['title'],
                description=request.form['description'],
                cost=float(request.form['cost']),
                markup_percentage=float(request.form['markup_percentage']),
                category=request.form['category'],
                vendor_name=request.form['vendor_name'],
                vendor_url=request.form['vendor_url'],
                stock_level=int(request.form['stock_level'])
            )
            product.update_price_from_markup()
            
            # Handle images
            image_urls = request.form.get('image_urls', '').split('\n')
            for idx, url in enumerate(image_urls):
                if url.strip():
                    image = ProductImage(
                        url=url.strip(),
                        is_primary=(idx == 0)
                    )
                    product.images.append(image)
            
            db.session.add(product)
            db.session.commit()
            flash('Product created successfully!', 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'danger')
    
    return render_template('admin/products/create.html')

@admin.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            product.sku = request.form['sku']
            product.title = request.form['title']
            product.description = request.form['description']
            product.cost = float(request.form['cost'])
            product.markup_percentage = float(request.form['markup_percentage'])
            product.category = request.form['category']
            product.vendor_name = request.form['vendor_name']
            product.vendor_url = request.form['vendor_url']
            product.stock_level = int(request.form['stock_level'])
            product.is_active = 'is_active' in request.form
            
            product.update_price_from_markup()
            
            # Handle images
            ProductImage.query.filter_by(product_id=product.id).delete()
            
            image_urls = request.form.get('image_urls', '').split('\n')
            for idx, url in enumerate(image_urls):
                if url.strip():
                    image = ProductImage(
                        url=url.strip(),
                        is_primary=(idx == 0)
                    )
                    product.images.append(image)
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
    
    return render_template('admin/products/edit.html', product=product)

@admin.route('/admin/products/<int:id>/delete', methods=['POST'])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))


@admin.route('/admin/products/export')
@admin_required
def export_products():
    format_type = request.args.get('format', 'csv')
    
    # Get all products with their images
    products = Product.query.all()
    
    data = []
    for product in products:
        # Get image URLs as comma-separated string
        image_urls = ','.join([img.url for img in product.images])
        
        data.append({
            'sku': product.sku,
            'title': product.title,
            'description': product.description,
            'category': product.category,
            'cost': product.cost,
            'markup_percentage': product.markup_percentage,
            'price': product.price,
            'stock_level': product.stock_level,
            'vendor_name': product.vendor_name,
            'vendor_url': product.vendor_url,
            'is_active': product.is_active,
            'image_urls': image_urls,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        })
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        # Create the response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=products_export.csv'}
        )
    
    elif format_type == 'excel':
        output = io.BytesIO()
        df = pd.DataFrame(data)
        df.to_excel(output, index=False, sheet_name='Products')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='products_export.xlsx'
        )

@admin.route('/admin/products/import', methods=['POST'])
@admin_required
def import_products():
    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('admin.products'))
    
    file = request.files['file']
    if not file.filename:
        flash('No file selected', 'danger')
        return redirect(url_for('admin.products'))
    
    try:
        # Read the file based on its extension
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            flash('Unsupported file format. Please upload CSV or Excel file.', 'danger')
            return redirect(url_for('admin.products'))
        
        success_count = 0
        error_count = 0
        error_messages = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Check if product exists (update if it does)
                product = Product.query.filter_by(sku=row['sku']).first()
                if not product:
                    product = Product()
                
                # Update product attributes
                product.sku = row['sku']
                product.title = row['title']
                product.description = row['description']
                product.category = row['category']
                product.cost = float(row['cost'])
                product.markup_percentage = float(row['markup_percentage'])
                product.stock_level = int(row['stock_level'])
                product.vendor_name = row['vendor_name']
                product.vendor_url = row['vendor_url']
                product.is_active = bool(row.get('is_active', True))
                
                product.update_price_from_markup()
                
                # Handle image URLs
                if 'image_urls' in row and row['image_urls']:
                    urls = str(row['image_urls']).split(',')
                    ProductImage.query.filter_by(product_id=product.id).delete()
                    for idx, url in enumerate(urls):
                        if url.strip():
                            image = ProductImage(
                                url=url.strip(),
                                is_primary=(idx == 0)
                            )
                            product.images.append(image)
                
                if not product.id:
                    db.session.add(product)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_messages.append(f"Error in row {index + 2}: {str(e)}")
                continue
        
        db.session.commit()
        
        # Show summary message
        message = f"Import complete: {success_count} products imported successfully."
        if error_count > 0:
            message += f" {error_count} errors occurred."
            for error in error_messages[:5]:  # Show first 5 errors
                flash(error, 'danger')
        
        flash(message, 'success')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))