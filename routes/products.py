from flask import Blueprint, render_template
from models.models_definitions import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)