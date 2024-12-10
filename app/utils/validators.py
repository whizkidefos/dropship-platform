def validate_product_data(row):
    """Validate product data from import"""
    errors = []
    
    # Required fields
    required_fields = ['sku', 'title', 'cost', 'markup_percentage']
    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            errors.append(f"Missing required field: {field}")
    
    # Data type validations
    try:
        if 'cost' in row:
            cost = float(row['cost'])
            if cost < 0:
                errors.append("Cost must be non-negative")
    except ValueError:
        errors.append("Invalid cost value")
    
    try:
        if 'markup_percentage' in row:
            markup = float(row['markup_percentage'])
            if markup < 0:
                errors.append("Markup percentage must be non-negative")
    except ValueError:
        errors.append("Invalid markup percentage value")
    
    try:
        if 'stock_level' in row:
            stock = int(row['stock_level'])
            if stock < 0:
                errors.append("Stock level must be non-negative")
    except ValueError:
        errors.append("Invalid stock level value")
    
    # URL validations
    if 'vendor_url' in row and row['vendor_url']:
        if not row['vendor_url'].startswith(('http://', 'https://')):
            errors.append("Vendor URL must start with http:// or https://")
    
    if 'image_urls' in row and row['image_urls']:
        urls = str(row['image_urls']).split(',')
        for url in urls:
            if url.strip() and not url.strip().startswith(('http://', 'https://')):
                errors.append("Image URLs must start with http:// or https://")
    
    return errors