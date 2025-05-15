import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, abort, current_app, flash
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
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
    from models.models_definitions import ProductImage

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])

        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template('merchant/add_product.html', errors=result), 400

        # إنشاء المنتج أولاً
        product = Product(
            name=result['name'],
            price=result['price'],
            description=result.get('description'),
            specs=result.get('specs'),
            merchant_id=session['user_id'],
            is_approved=False
        )
        sequence = Product.query.filter_by(merchant_id=session['user_id']).count() + 1
        product.generate_code(sequence)

        try:
            db.session.add(product)
            db.session.flush()  # للحصول على product.id قبل رفع الصور

            # رفع الصور
            files = request.files.getlist('images')
            for index, file in enumerate(files):
                if file and file.filename:
                    upload_result = cloudinary.uploader.upload(file)
                    image_url = upload_result.get('secure_url')
                    img = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=(index == 0)
                    )
                    db.session.add(img)

            db.session.commit()

            # إشعار المشرف
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

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ Error saving product: {e}")
            return "Unexpected error", 500

    return render_template('merchant/add_product.html')



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
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
    from models.models_definitions import ProductImage

    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])

        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template('merchant/edit_product.html', product=product, errors=result), 400

        product.name = result['name']
        product.price = result['price']
        product.description = result.get('description')
        product.specs = result.get('specs')
        product.is_approved = False

        # تحديث الصورة الافتراضية
        main_image_id = request.form.get('main_image_id')
        if main_image_id:
            for img in product.images:
                img.is_main = (str(img.id) == main_image_id)

        # رفع صور جديدة
        new_images = request.files.getlist('images')
        for file in new_images:
            if file and file.filename:
                try:
                    upload_result = cloudinary.uploader.upload(file)
                    image_url = upload_result.get('secure_url')
                    img = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=False
                    )
                    db.session.add(img)
                except Exception as e:
                    current_app.logger.error(f"Error uploading image: {e}")
                    return "Error uploading image", 500

        db.session.commit()
        return redirect(url_for('merchant.my_products'))

    return render_template('merchant/edit_product.html', product=product)


@merchant_bp.route('/products')
@login_required
@merchant_required
def my_products():
    """Display a list of products owned by the merchant."""
    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)


@merchant_bp.route('/products/<int:product_id>/edit-image', methods=['GET'])
@login_required
@merchant_required
def edit_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)
    return render_template('shared/edit_image.html', product=product)


@merchant_bp.route('/products/<int:product_id>/save-image', methods=['POST'])
@login_required
@merchant_required
def save_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)

    image_data = request.form.get('image_data')
    if not image_data:
        flash("❌ لم يتم استلام الصورة الجديدة", "error")
        return redirect(url_for('merchant.edit_product_image', product_id=product_id))

    # رفع الصورة إلى Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(image_data)
        product.image = upload_result['secure_url']
        db.session.commit()
        flash("✅ تم تحديث صورة المنتج بنجاح", "success")
    except Exception as e:
        current_app.logger.error(f"Error uploading new product image: {e}")
        flash("❌ حدث خطأ أثناء رفع الصورة الجديدة", "error")

    return redirect(url_for('merchant.edit_product', product_id=product.id))
