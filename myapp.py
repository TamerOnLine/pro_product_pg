import os
from flask import Flask
from models.models import db
from routes import main_routes
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    # تحميل مفتاح الجلسة من ملف .env
    app.secret_key = os.getenv('cv_kay')  # تأكد أن الاسم في .env يطابقه

    # ✅ إعدادات رفع الصور
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # الحد الأقصى 2MB

    # إعداد قاعدة البيانات
    db_path = os.path.join(basedir, 'instance', 'products.db')
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main_routes)

    return app


app = create_app()

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8030)
