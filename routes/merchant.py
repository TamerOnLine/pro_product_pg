from flask import Blueprint, render_template, request, redirect, url_for, session
from models.models_definitions import Product, db
from routes.auth_utils import login_required
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from models.models_definitions import User

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403
    return render_template('merchant/dashboard.html', username=session['username'])


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
            image_url, _ = cloudinary_url(public_id, quality="auto", fetch_format="auto", crop="limit", width=800, height=800)

        product = Product(
            product_code=request.form['product_code'],
            name=request.form['name'],
            price=float(request.form['price']),
            description=request.form.get('description'),
            specs=request.form.get('specs'),
            image=image_url,
            merchant_id=session['user_id'],
            is_approved=False
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('merchant.dashboard'))

    return render_template('merchant/add_product.html')


@merchant_bp.route('/products')
@login_required
def my_products():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)


@merchant_bp.route('/profile')
@login_required
def profile():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    user = User.query.get_or_404(session['user_id'])
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username'].strip()
        user.email = request.form['email'].strip()
        db.session.commit()
        return redirect(url_for('merchant.profile'))  # ✅ يعود إلى صفحة بياناتي

    return render_template('merchant/edit_profile.html', user=user)

