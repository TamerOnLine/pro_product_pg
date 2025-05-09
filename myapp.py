import os
from flask import Flask, render_template, g
from models.models_definitions import db
from routes import register_routes
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader


load_dotenv()

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = os.getenv('cv_kay')

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

    # Configure TinyMCE API key
    app.config['TINYMCE_API_KEY'] = os.getenv('TINYMCE_API_KEY')

    # Set image upload folder for Render environment
    app.config['UPLOAD_FOLDER'] = os.path.join('/tmp', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

    # Configure PostgreSQL database
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        raise RuntimeError("DATABASE_URL not found in .env or Render settings.")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    register_routes(app)

    return app


app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    """
    Render the 404 error page.

    Args:
        e (Exception): The exception raised.

    Returns:
        Tuple: Rendered 404 template and status code.
    """
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    Render the 500 error page.

    Args:
        e (Exception): The exception raised.

    Returns:
        Tuple: Rendered 500 template and status code.
    """
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden(e):
    """
    Render the 403 error page.

    Args:
        e (Exception): The exception raised.

    Returns:
        Tuple: Rendered 403 template and status code.
    """
    return render_template('errors/403.html'), 403


def create_super_admin_if_needed():
    """
    Create a super admin user if none exists.
    """
    from models.models_definitions import User

    if User.query.filter_by(role='admin').first():
        print("Owner account already exists.")
        return

    print("Creating Super Admin account")
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    admin = User(username=username, email=email, role='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Super Admin account created successfully.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_super_admin_if_needed()
    app.run(debug=True, host='0.0.0.0', port=8030)
