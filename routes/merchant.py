from flask import Blueprint, render_template, request, redirect, url_for, session
from models.models_definitions import Product, db, User
from routes.auth_utils import login_required
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Render the merchant dashboard if user role is 'merchant'.

    Returns:
        Rendered HTML template or unauthorized error page.
    """
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403
    return render_template('merchant/dashboard.html',
                           username=session['username'])


@merchant_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    if request.method == 'POST':
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
            name=request.form['name'],
            price=float(request.form['price']),
            description=request.form.get('description'),
            specs=request.form.get('specs'),
            image=image_url,
            merchant_id=session['user_id'],
            is_approved=False
        )

        # ✅ توليد كود المنتج بناءً على التسلسل والتاجر
        sequence = Product.query.filter_by(merchant_id=session['user_id']).count() + 1
        product.generate_code(sequence)

        db.session.add(product)
        db.session.commit()
        return redirect(url_for('merchant.dashboard'))

    return render_template(
        'merchant/add_product.html',
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )



@merchant_bp.route('/products')
@login_required
def my_products():
    """
    Display the list of products added by the merchant.

    Returns:
        Rendered HTML template with list of merchant's products.
    """
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)


@merchant_bp.route('/profile')
@login_required
def profile():
    """
    Display the merchant's profile page.

    Returns:
        Rendered HTML template with user information.
    """
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    user = User.query.get_or_404(session['user_id'])
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Allow the merchant to edit their profile.

    Methods:
        GET: Display profile edit form.
        POST: Save updated profile info to database.

    Returns:
        Rendered HTML template or redirect to profile page.
    """
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username'].strip()
        user.email = request.form['email'].strip()
        db.session.commit()
        return redirect(url_for('merchant.profile'))

    return render_template('merchant/edit_profile.html', user=user)
