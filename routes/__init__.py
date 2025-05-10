from routes.products import products_bp
from routes.admin import admin_bp
from routes.reset import reset_bp
from routes.user_auth import user_auth_bp
from routes.merchant import merchant_bp

def register_routes(app):
    """
    Register all application routes using Flask Blueprints.

    Args:
        app (Flask): The Flask application instance.

    This function attaches the defined route Blueprints to the Flask app.
    The admin routes are prefixed with '/admin'.
    """
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(reset_bp)
    app.register_blueprint(user_auth_bp)
    app.register_blueprint(merchant_bp)
