import os
from myapp import create_app
from models.models_definitions import db

# مرّر رابط PostgreSQL هنا (من Render - Internal Database URL)
DATABASE_URL = os.environ.get('DATABASE_URL')
print("DATABASE_URL:", DATABASE_URL)

# أنشئ التطبيق
app = create_app()

# أعد ضبط الاتصال داخل هذا السياق (override)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# أنشئ الجداول داخل PostgreSQL
with app.app_context():
    db.create_all()
    print("✅ تم إنشاء الجداول بنجاح في قاعدة بيانات PostgreSQL!")
