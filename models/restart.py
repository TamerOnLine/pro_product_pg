# restart.py
from myapp import app
from models.models import db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ قاعدة البيانات أُعيد إنشاؤها بنجاح.")
