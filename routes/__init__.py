import os

from flask import Blueprint, render_template, request, redirect, url_for, session
from models.models import Product, db
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from functools import wraps
from routes.auth_utils import login_required
from werkzeug.utils import secure_filename
import uuid
from flask import current_app





main_routes = Blueprint('main', __name__)

@main_routes.before_app_request
def protect_admin_routes():
    from flask import request, session, redirect, url_for
    if request.path.startswith('/admin'):
        if not session.get('logged_in') and not request.path.startswith('/admin/login'):
            return redirect(url_for('main.login'))


@main_routes.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@main_routes.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')


# السماح فقط بأنواع معينة من الصور
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_routes.route('/admin/add', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'POST':
        file = request.files['image']
        image_filename = None

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            image_filename = unique_name

        product = Product(
            product_code=request.form['product_code'],
            name=request.form['name'],
            price=float(request.form['price']),
            description=request.form.get('description'),
            image=image_filename,
            specs=request.form.get('specs')
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('admin/add_product.html')



@main_routes.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@main_routes.route('/admin/products')
def admin_products():
    products = Product.query.all()
    return render_template('admin/admin_products.html', products=products)

@main_routes.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.product_code = request.form['product_code']
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.specs = request.form['specs']
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            product.image = unique_name
        
        db.session.commit()
        return redirect(url_for('main.admin_products'))

    return render_template('admin/edit_product.html', product=product)


@main_routes.route('/admin/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('main.admin_products'))

@main_routes.route('/admin/reset_db', methods=['POST'])
def reset_db():
    # حذف كل الجداول وإعادة إنشائها بشكل رسمي وآمن
    db.drop_all()
    db.create_all()
    return "✅ تم حذف كل الجداول وإعادة إنشائها بالكامل.", 200

@main_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('main.admin_dashboard'))
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة'
    return render_template('admin/login.html', error=error)
