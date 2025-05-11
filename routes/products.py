from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.models_definitions import db, Product
import cloudinary.uploader





products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def index():
    """
    Render the homepage with a list of approved products.

    Returns:
        str: Rendered HTML of the homepage with approved products.
    """
    products = Product.query.filter_by(is_approved=True).all()
    return render_template('index.html', products=products)


@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Render the detail page for a specific product by ID.

    Args:
        product_id (int): The ID of the product to display.

    Returns:
        str: Rendered HTML of the product detail page.
    """
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)




# دالة لحساب التسلسل الجديد للعميل
def get_next_sequence_for_merchant(merchant_id):
    count = Product.query.filter_by(merchant_id=merchant_id).count()
    return count + 1

@products_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    try:
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form.get('description')
        specs = request.form.get('specs')
        image = request.files.get('image')  # صورة من النموذج
        merchant_id = 1  # عدّل لاحقًا لربطه بالمستخدم الحالي

        sequence = get_next_sequence_for_merchant(merchant_id)

        # ✅ رفع الصورة إلى Cloudinary
        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get('secure_url')

        # ✅ إنشاء المنتج وتخزين رابط الصورة
        product = Product(
            name=name,
            price=price,
            description=description,
            specs=specs,
            image=image_url,
            merchant_id=merchant_id
        )
        product.generate_code(sequence)

        db.session.add(product)
        db.session.commit()

        flash(f"✅ تمت إضافة المنتج بكود: {product.product_code}")
        return redirect(url_for('admin.admin_dashboard'))


    except Exception as e:
        print("❌ حدث خطأ أثناء إضافة المنتج:", e)
        return "An error occurred while adding the product."

