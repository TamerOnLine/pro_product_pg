import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, current_app, session
)
from models.models_definitions import Product, db
from werkzeug.utils import secure_filename
from routes.auth_utils import login_required, admin_only
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from logic.notifications import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_email, validate_password, sanitize_text, validate_price



admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): Name of the file to check.

    Returns:
        bool: True if file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/')
@admin_only
@login_required
def admin_dashboard():
    """Render the admin dashboard page."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/products')
@admin_only
@login_required
def admin_products():
    """Display a list of all products."""
    products = Product.query.all()
    return render_template('admin/admin_products.html', products=products)


@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_only
@login_required
def admin_add_product():
    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        from logic.validation_utils import validate_form

        is_valid, result = validate_form(data, schema, sanitize_fields=['name', 'description', 'specs'])

        if not is_valid:
            return str(result), 400

        file = request.files.get('image')
        image_url = None

        if file and file.filename != '':
            upload_result = cloudinary.uploader.upload(file)
            public_id = upload_result['public_id']
            image_url, options = cloudinary_url(
                public_id,
                quality="auto",
                fetch_format="auto",
                crop="limit",
                width=800,
                height=800
            )

        try:
            sequence = Product.query.count() + 1

            product = Product(
                name=result['name'],
                price=result['price'],
                description=result.get('description'),
                image=image_url,
                specs=result.get('specs'),
                merchant_id=session.get("user_id")
            )
            product.generate_code(sequence)

            db.session.add(product)
            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))

        except Exception as e:
            current_app.logger.exception("❌ حدث استثناء أثناء إضافة المنتج")
            return "حدث خطأ غير متوقع. الرجاء المحاولة لاحقًا.", 500

    return render_template(
        'admin/add_product.html',
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )



@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_only
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        from logic.validation_utils import validate_form

        is_valid, result = validate_form(data, schema, sanitize_fields=['name', 'description', 'specs'])

        if not is_valid:
            return str(result), 400

        product.name = result['name']
        product.price = result['price']
        product.description = result.get('description')
        product.specs = result.get('specs')
        product.is_approved = False

        file = request.files.get('image')
        if file and file.filename != '':
            upload_result = cloudinary.uploader.upload(file)
            public_id = upload_result['public_id']
            image_url, options = cloudinary_url(
                public_id,
                quality="auto",
                fetch_format="auto",
                crop="limit",
                width=800,
                height=800
            )
            product.image = image_url

        db.session.commit()
        return redirect(url_for('admin.admin_products'))

    return render_template(
        'admin/edit_product.html',
        product=product,
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )


@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@admin_only
@login_required
def delete_product(product_id):
    """
    Delete a product from the database.

    Args:
        product_id (int): ID of the product to delete.

    Returns:
        Response: Redirect to product list.
    """
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.admin_products'))


@admin_bp.route('/system-links')
@admin_only
@login_required
def system_links():
    """Render the system links page."""
    return render_template('admin/system_links.html')




@admin_bp.route('/approve/<int:product_id>', methods=['POST'])
@admin_only
@login_required
def approve_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_approved = True
    db.session.commit()



    advance_notification(
        product_id=product.id,
        from_role='admin',
        from_type='product_edited',
        to_user_id=product.merchant_id,
        to_role='merchant',
        to_type='product_approved',
        message=f"✅ تم اعتماد منتجك: {product.name}"
    )



    return redirect(url_for('admin.admin_products'))
