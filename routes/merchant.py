from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from models.models_definitions import Product, db, User
from routes.auth_utils import login_required
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from logic.notifications import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_email, validate_password, sanitize_text, validate_price


merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'merchant':
        abort(403)
    return render_template('merchant/dashboard.html', username=session['username'])


@merchant_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if session.get('role') != 'merchant':
        abort(403)

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        from logic.validation_utils import validate_form  # تأكد من الاستيراد

        is_valid, result = validate_form(data, schema, sanitize_fields=['name', 'description', 'specs'])

        if not is_valid:
            return str(result), 400

        file = request.files.get('image')
        image_url = None

        if file and file.filename:
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

        db.session.add(product)
        db.session.commit()

        advance_notification(
            product_id=product.id,
            from_role=None,
            from_type=None,
            to_user_id=None,
            to_role='admin',
            to_type='product_edited',
            message=f"📝 منتج جديد من التاجر {session['username']} بانتظار الموافقة"
        )

        return redirect(url_for('merchant.dashboard'))

    return render_template(
        'merchant/add_product.html',
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )



@merchant_bp.route('/profile')
@login_required
def profile():
    if session.get('role') != 'merchant':
        abort(403)

    user = User.query.get_or_404(session['user_id'])
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if session.get('role') != 'merchant':
        abort(403)

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username'].strip()
        user.email = request.form['email'].strip()
        db.session.commit()
        return redirect(url_for('merchant.profile'))

    return render_template('merchant/edit_profile.html', user=user)


@merchant_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if session.get('role') != 'merchant':
        abort(403)

    product = Product.query.get_or_404(product_id)

    if product.merchant_id != session['user_id']:
        abort(403)

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
        product.is_approved = False  # يحتاج موافقة جديدة

        image = request.files.get('image')
        if image and image.filename:
            upload_result = cloudinary.uploader.upload(image)
            product.image = upload_result.get('secure_url')

        db.session.commit()
        return redirect(url_for('merchant.my_products'))

    return render_template(
        'merchant/edit_product.html',
        product=product,
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )

@merchant_bp.route('/products')
@login_required
def my_products():
    if session.get('role') != 'merchant':
        abort(403)

    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)

