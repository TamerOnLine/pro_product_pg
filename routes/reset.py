from flask import Blueprint
from models.models_definitions import db

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/admin/reset_db', methods=['POST'])
def reset_db():
    db.drop_all()
    db.create_all()
    return "✅ تم حذف كل الجداول وإعادة إنشائها بالكامل.", 200

@reset_bp.route('/dev/reset')
def dev_reset():
    db.drop_all()
    db.create_all()
    return "✅ قاعدة البيانات أُعيد تعيينها بدون الحاجة لتسجيل الدخول (خاص بالتطوير فقط)"
