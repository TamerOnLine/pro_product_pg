# app.py
import os
from flask import Flask
from models.models import db
from routes import register_routes
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from flask import g



load_dotenv()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv('cv_kay')

    # ✅ إعداد Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")

    )

    # ✅ إعداد مفتاح TinyMCE
    app.config['TINYMCE_API_KEY'] = os.getenv('TINYMCE_API_KEY')


    # ✅ حفظ الصور في مجلد مؤقت مناسب لـ Render
    app.config['UPLOAD_FOLDER'] = os.path.join('/tmp', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

    # ✅ قاعدة البيانات: PostgreSQL من متغير البيئة
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        raise RuntimeError("❌ لم يتم العثور على DATABASE_URL في .env أو إعدادات Render.")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    register_routes(app)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8030)
