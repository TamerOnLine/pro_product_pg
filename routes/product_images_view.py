

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from models.models_definitions import db, ProductImage, Product
from routes.auth_utils import login_required
import cloudinary.uploader
from flask import current_app



product_images_bp = Blueprint('product_images', __name__)


@product_images_bp.route('/products/<int:product_id>/images')
@login_required
def manage_product_images(product_id):
    product = Product.query.get_or_404(product_id)

    # استخراج الدور والمعرّف من الجلسة
    role = session.get('role')
    user_id = session.get('user_id')

    # 🔒 حماية: التاجر يرى فقط منتجاته
    if role == 'merchant' and product.merchant_id != user_id:
        current_app.logger.warning(f"🛑 Unauthorized access by merchant {user_id} to product {product_id}")
        abort(403)

    # ✅ طباعة تشخيصية (اختياري أثناء التطوير)
    print("🔍 ROLE:", role)
    print("🔍 USER ID:", user_id)
    print("🔍 PRODUCT:", product.name)
    print("🔍 IMAGE COUNT:", len(product.images))

    return render_template('shared/manage_images.html', product=product)



@product_images_bp.route('/images/<int:image_id>/set-main', methods=['POST'])
@login_required
def set_main_image(image_id):
    img = ProductImage.query.get_or_404(image_id)
    product = img.product

    # 🔒 حماية حسب الدور
    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    # ✅ تعيين الرئيسية
    for i in product.images:
        i.is_main = (i.id == image_id)

    db.session.commit()
    flash("✅ تم تعيين الصورة كصورة رئيسية", "success")
    return redirect(request.referrer or url_for('merchant.my_products'))




@product_images_bp.route('/products/<int:product_id>/upload', methods=['POST'])
@login_required
def upload_image(product_id):
    product = Product.query.get_or_404(product_id)

    # صلاحية الوصول
    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("❌ لا يوجد ملف مرفوع", "error")
        return redirect(request.referrer)

    try:
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('secure_url')

        from models.models_definitions import ProductImage, db
        new_image = ProductImage(
            product_id=product.id,
            image_url=image_url,
            is_main=False
        )
        db.session.add(new_image)
        db.session.commit()
        flash("✅ تم رفع الصورة بنجاح", "success")

    except Exception as e:
        current_app.logger.error(f"❌ Error uploading image: {e}")
        flash("حدث خطأ أثناء رفع الصورة", "error")

    return redirect(request.referrer or url_for('merchant.my_products'))


@product_images_bp.route('/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    img = ProductImage.query.get_or_404(image_id)
    product = img.product

    # صلاحية الوصول
    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    try:
        db.session.delete(img)
        db.session.commit()
        flash("🗑️ تم حذف الصورة بنجاح", "success")
    except Exception as e:
        current_app.logger.error(f"❌ Error deleting image: {e}")
        flash("حدث خطأ أثناء حذف الصورة", "error")

    return redirect(request.referrer or url_for('merchant.my_products'))
