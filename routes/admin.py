import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from models.models_definitions import Product, db
from werkzeug.utils import secure_filename
from routes.auth_utils import login_required
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from routes.auth_utils import login_required, admin_only


admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/')
@admin_only
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/products')
@admin_only
@login_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/admin_products.html', products=products)

@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_only
@login_required
def admin_add_product():
    if request.method == 'POST':
        file = request.files.get('image')
        image_url = None

        if file and file.filename != '' and allowed_file(file.filename):
            upload_result = cloudinary.uploader.upload(file)
            public_id = upload_result['public_id']
            image_url, options = cloudinary_url(public_id, quality="auto", fetch_format="auto", crop="limit", width=800, height=800)

        try:
            product = Product(
                product_code=request.form['product_code'],
                name=request.form['name'],
                price=float(request.form['price']),
                description=request.form.get('description'),
                image=image_url,
                specs=request.form.get('specs')
            )
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            print(f"❌ خطأ أثناء إضافة المنتج: {e}")
            return "حدث خطأ أثناء إضافة المنتج.", 500

    return render_template('admin/add_product.html', tinymce_api_key=os.getenv('TINYMCE_API_KEY'))


@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_only
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.product_code = request.form['product_code']
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form.get('description')
        product.specs = request.form.get('specs')

        file = request.files.get('image')
        if file and file.filename != '' and allowed_file(file.filename):
            upload_result = cloudinary.uploader.upload(file)
            public_id = upload_result['public_id']
            image_url, options = cloudinary_url(public_id, quality="auto", fetch_format="auto", crop="limit", width=800, height=800)
            product.image = image_url

        db.session.commit()
        return redirect(url_for('admin.admin_products'))

    return render_template('admin/edit_product.html', product=product, tinymce_api_key=os.getenv('TINYMCE_API_KEY'))



@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@admin_only
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.admin_products'))

@admin_bp.route('/system-links')
@admin_only
@login_required
def system_links():
    return render_template('admin/system_links.html')

