import os
import getpass
from datetime import datetime

from flask import Flask, render_template, g, session, request
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

from models.models_definitions import db, User
from routes import register_routes
from config.logging_config import setup_logging
from routes import register_error_handlers, register_routes
from flask_babel import Babel
from flask_babel import get_locale as babel_get_locale
from flask import redirect, url_for, request, session


load_dotenv()
babel = Babel()

def select_locale():
    return session.get('lang') or request.accept_languages.best_match(['en', 'ar', 'de'])


    

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    setup_logging(app)
    babel.init_app(app, locale_selector=select_locale)
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    app.jinja_env.globals['get_locale'] = select_locale
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
    register_error_handlers(app)

    return app


app = create_app()

@app.route("/set_language/<lang>")
def set_language(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("index"))




@app.context_processor
def inject_current_year():
    """
    Inject the current year into all templates.

    Returns:
        dict: Dictionary with the current year.
    """
    return {'current_year': datetime.utcnow().year}


@app.context_processor
def inject_globals():
    """
    Inject global variables into all templates.

    Returns:
        dict: Dictionary with site branding.
    """
    return {
        'site_brand': 'منتجي'  # This can be changed to any name later.
    }


@app.context_processor
def inject_unread_notifications():
    from logic.notification_service import get_user_notifications
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')
    notifications = get_user_notifications(role, user_id)
    unread_count = sum(1 for n in notifications if not n.is_read)
    return dict(unread_count=unread_count)


def create_super_admin_if_needed():
    """
    Create a super admin user if none exists.

    Checks if an admin user already exists. If not, prompts the user
    to input credentials and creates a new admin user.
    """
    from models.models_definitions import User

    # Check if an admin already exists
    if User.query.filter_by(role='admin').first():
        print("An owner account already exists. No need to create one.")
        return

    # Prompt for input only if admin does not exist
    print("Creating a Super Admin account")
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        print("This username or email is already in use.")
        return

    password = getpass.getpass("Enter password (input hidden): ").strip()

    admin = User(username=username, email=email, role='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Super Admin account has been created successfully.")


if __name__ == '__main__':
    # Set the environment first
    app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

    # Ensure operations run within the application context (app context)
    with app.app_context():
        if app.config['ENV'] == 'development':  # Ensure these operations are only executed in development environment
            db.create_all()
            create_super_admin_if_needed()

    # Run the app based on the environment
    debug_mode = app.config['ENV'] == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=8030)

