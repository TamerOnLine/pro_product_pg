import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, abort, current_app
)
from models.models_definitions import Product, db, User
from routes.auth_utils import login_required
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from logic.notification_service import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_email, validate_password, sanitize_text, validate_price
from functools import wraps
from logic.validation_utils import validate_form


merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')

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

def merchant_required(f):
    """
    Decorator to ensure that the user is a merchant.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'merchant':
            current_app.logger.warning(f"Unauthorized access attempt by user {session.get('username')}")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@merchant_bp.route('/dashboard')
@login_required
@merchant_required
def dashboard():
    """Render the merchant dashboard page."""
    return render_template('merchant/dashboard.html', username=session['username'])


@merchant_bp.route('/add', methods=['GET', 'POST'])
@login_required
@merchant_required
def add_product():
    from logic.validation_utils import validate_form, coerce_price

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {
                'type': 'float',
                'min': 0,
                'required': True,
                'coerce': coerce_price  # ✅ تحويل السعر تلقائيًا
            },
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])

        from logic.validation_utils import sanitize_rich_text
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template(
                'merchant/add_product.html',
                errors=result,
                tinymce_api_key=os.getenv('TINYMCE_API_KEY')
            ), 400

        file = request.files.get('image')
        image_url = None

        if file and file.filename:
            try:
                upload_result = cloudinary.uploader.upload(file)
                public_id = upload_result['public_id']
                image_url, _ = cloudinary_url(
                    public_id,
                    quality="auto",
                    fetch_format="auto",
                    crop="limit",
                    width=800,
                    height=800
                )
            except Exception as e:
                current_app.logger.error(f"Cloudinary upload error: {e}")
                return "Error uploading image. Please try again later.", 500

        product = Product(
            name=result['name'],
            price=result['price'],
            description=result.get('description'),
            specs=result.get('specs'),
            image=image_url,
            merchant_id=session['user_id'],
            is_approved=False
        )

        sequence = Product.query.filter_by(merchant_id=session['user_id']).count() + 1
        product.generate_code(sequence)

        try:
            db.session.add(product)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error saving product to database: {e}")
            return "An unexpected error occurred. Please try again later.", 500

        # إشعار المشرف بمنتج جديد
        advance_notification(
            product_id=product.id,
            from_role=None,
            from_type=None,
            to_user_id=None,
            to_role='admin',
            to_type='product_edited',
            message=f"📝 New product from merchant {session['username']} awaiting approval"
        )

        return redirect(url_for('merchant.dashboard'))

    return render_template(
        'merchant/add_product.html',
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )



@merchant_bp.route('/profile')
@login_required
@merchant_required
def profile():
    """Render the merchant's profile page."""
    user = User.query.get_or_404(session['user_id'])
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@merchant_required
def edit_profile():
    """Edit the merchant's profile."""
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username'].strip()
        user.email = request.form['email'].strip()
        db.session.commit()
        return redirect(url_for('merchant.profile'))

    return render_template('merchant/edit_profile.html', user=user)



@merchant_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@merchant_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.merchant_id != session['user_id']:
        abort(403)

    if request.method == 'POST':
        from logic.validation_utils import validate_form, coerce_price

        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {
                'type': 'float',
                'min': 0,
                'required': True,
                'coerce': coerce_price
            },
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])

        from logic.validation_utils import sanitize_rich_text
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template(
                'merchant/edit_product.html',
                product=product,
                errors=result,
                tinymce_api_key=os.getenv('TINYMCE_API_KEY')
            ), 400

        product.name = result['name']
        product.price = result['price']
        product.description = result.get('description')
        product.specs = result.get('specs')
        product.is_approved = False

        image = request.files.get('image')
        if image and image.filename:
            try:
                upload_result = cloudinary.uploader.upload(image)
                product.image = upload_result.get('secure_url')
            except Exception as e:
                current_app.logger.error(f"Error uploading image to Cloudinary: {e}")
                return "Error uploading image. Please try again later.", 500

        db.session.commit()
        return redirect(url_for('merchant.my_products'))

    return render_template(
        'merchant/edit_product.html',
        product=product,
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )



@merchant_bp.route('/products')
@login_required
@merchant_required
def my_products():
    """Display a list of products owned by the merchant."""
    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)
