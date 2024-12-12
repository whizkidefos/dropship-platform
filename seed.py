from app import create_app, db
from app.models.product import Product, ProductImage

def seed_products():
    app = create_app()
    with app.app_context():
        products = [
            {
                'sku': 'TECH-001',
                'title': 'Wireless Noise-Cancelling Headphones',
                'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear sound quality.',
                'cost': 150.00,
                'markup_percentage': 40,
                'category': 'Electronics',
                'vendor_name': 'TechGear',
                'vendor_url': 'https://example.com',
                'stock_level': 50,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Headphones+Main',
                    'https://via.placeholder.com/800x800.png?text=Headphones+Side',
                    'https://via.placeholder.com/800x800.png?text=Headphones+Case'
                ]
            },
            {
                'sku': 'HOME-001',
                'title': 'Smart LED Desk Lamp',
                'description': 'Adjustable LED desk lamp with wireless charging base, multiple lighting modes, and smartphone control.',
                'cost': 45.00,
                'markup_percentage': 55,
                'category': 'Home & Office',
                'vendor_name': 'SmartHome',
                'stock_level': 75,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Desk+Lamp'
                ]
            },
            {
                'sku': 'FASHION-001',
                'title': 'Minimalist Leather Watch',
                'description': 'Classic minimalist watch with genuine leather strap, Japanese movement, and water resistance.',
                'cost': 80.00,
                'markup_percentage': 60,
                'category': 'Fashion',
                'vendor_name': 'TimePiece',
                'stock_level': 30,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Watch+Front',
                    'https://via.placeholder.com/800x800.png?text=Watch+Side'
                ]
            },
            {
                'sku': 'TECH-002',
                'title': 'Ultra-Slim Power Bank',
                'description': '10000mAh power bank with fast charging, dual USB ports, and compact design.',
                'cost': 25.00,
                'markup_percentage': 45,
                'category': 'Electronics',
                'vendor_name': 'TechGear',
                'stock_level': 100,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Power+Bank'
                ]
            },
            {
                'sku': 'HOME-002',
                'title': 'Aromatherapy Diffuser',
                'description': '300ml essential oil diffuser with LED mood lighting, timer settings, and automatic shut-off.',
                'cost': 30.00,
                'markup_percentage': 50,
                'category': 'Home & Office',
                'vendor_name': 'WellLife',
                'stock_level': 60,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Diffuser+White',
                    'https://via.placeholder.com/800x800.png?text=Diffuser+Black'
                ]
            },
            {
                'sku': 'FASHION-002',
                'title': 'Crossbody Phone Bag',
                'description': 'Compact crossbody bag perfect for phones and essentials, made with premium vegan leather.',
                'cost': 35.00,
                'markup_percentage': 65,
                'category': 'Fashion',
                'vendor_name': 'StyleCo',
                'stock_level': 45,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Bag+Front',
                    'https://via.placeholder.com/800x800.png?text=Bag+Inside'
                ]
            },
            {
                'sku': 'TECH-003',
                'title': 'Smart WiFi Security Camera',
                'description': '1080p HD security camera with night vision, motion detection, and two-way audio.',
                'cost': 55.00,
                'markup_percentage': 45,
                'category': 'Electronics',
                'vendor_name': 'SmartHome',
                'stock_level': 40,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Camera'
                ]
            },
            {
                'sku': 'HOME-003',
                'title': 'Premium Coffee Grinder',
                'description': 'Adjustable burr coffee grinder with 15 grind settings and premium stainless steel design.',
                'cost': 65.00,
                'markup_percentage': 50,
                'category': 'Home & Office',
                'vendor_name': 'KitchenPro',
                'stock_level': 25,
                'images': [
                    'https://via.placeholder.com/800x800.png?text=Grinder+Front',
                    'https://via.placeholder.com/800x800.png?text=Grinder+Top'
                ]
            }
        ]

        for product_data in products:
            # Check if product already exists
            if not Product.query.filter_by(sku=product_data['sku']).first():
                product = Product(
                    sku=product_data['sku'],
                    title=product_data['title'],
                    description=product_data['description'],
                    cost=product_data['cost'],
                    markup_percentage=product_data['markup_percentage'],
                    category=product_data['category'],
                    vendor_name=product_data['vendor_name'],
                    vendor_url=product_data.get('vendor_url', 'https://example.com'),
                    stock_level=product_data['stock_level']
                )
                product.update_price_from_markup()

                # Add images
                for idx, url in enumerate(product_data['images']):
                    image = ProductImage(
                        url=url,
                        is_primary=(idx == 0)
                    )
                    product.images.append(image)

                db.session.add(product)

        db.session.commit()
        print("Test products have been added to the database.")

if __name__ == '__main__':
    seed_products()