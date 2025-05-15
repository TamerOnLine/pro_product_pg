from flask import Blueprint, request, session, current_app, render_template, redirect, url_for, flash
from models.models_definitions import db, Product
import cloudinary.uploader


products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    try:
        products = Product.query.filter_by(is_approved=True).all()
        return render_template('index.html', products=products)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Internal error: {e}", 500
 

@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Render the detail page for a specific product by ID.

    Args:
        product_id (int): The ID of the product to display.

    Returns:
        str: Rendered HTML of the product detail page.
    """
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('product_detail.html', product=product)
    except Exception as e:
        import traceback
        traceback.print_exc()  # ستطبع الخطأ بالتفصيل في الطرفية
        return f"Internal Error: {str(e)}", 500

# Function to calculate the next sequence number for a merchant
def get_next_sequence_for_merchant(merchant_id):
    count = Product.query.filter_by(merchant_id=merchant_id).count()
    return count + 1

@products_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    try:
        # Getting the form data
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form.get('description')
        specs = request.form.get('specs')
        image = request.files.get('image')  # Image from the form
        merchant_id = 1  # Later, change this to link with the current authenticated user

        # Validate required fields
        if not name or not price:
            flash("❌ Product name and price are required.", "error")
            return redirect(url_for('products.index'))

        # Get next product sequence number
        sequence = get_next_sequence_for_merchant(merchant_id)

        # Image upload to Cloudinary
        image_url = None
        if image:
            try:
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                current_app.logger.error(f"Error uploading image to Cloudinary: {e}")
                flash("❌ Error uploading image. Please try again later.", "error")
                return redirect(url_for('products.index'))

        # Create product and store image URL
        product = Product(
            name=name,
            price=price,
            description=description,
            specs=specs,
            image=image_url,
            merchant_id=merchant_id
        )
        product.generate_code(sequence)

        # Add product to the database
        db.session.add(product)
        db.session.commit()

        flash(f"✅ Product added successfully with code: {product.product_code}", "success")
        return redirect(url_for('admin.admin_dashboard'))

    except Exception as e:
        current_app.logger.exception("❌ Error during product creation")
        flash("❌ An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('products.index'))


