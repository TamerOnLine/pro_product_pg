from routes.products import products_bp
from routes.admin import admin_bp
from routes.reset import reset_bp
from routes.user_auth import user_auth_bp
from routes.merchant import merchant_bp
from routes.notifications import notifications_bp
from flask import render_template
from werkzeug.routing import BuildError
from routes.test_errors import test_errors_bp

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
    app.register_blueprint(notifications_bp)
    app.register_blueprint(test_errors_bp)

   
def register_error_handlers(app):
    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(BuildError)
    def handle_build_error(e):
        return render_template("errors/500.html"), 500
    
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

