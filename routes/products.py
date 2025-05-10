from flask import Blueprint, render_template
from models.models_definitions import Product

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
