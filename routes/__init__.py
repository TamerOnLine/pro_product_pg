from routes.products import products_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.reset import reset_bp

# هذا الملف لتجميع كل المسارات المسجلة عبر Blueprints
# وتسجيلها في التطبيق من خلال app.register_blueprint(...) في myapp.py

def register_routes(app):
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp)
    app.register_blueprint(reset_bp)
