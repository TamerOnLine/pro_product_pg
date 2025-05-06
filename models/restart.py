@main_routes.route('/dev/reset')
def dev_reset():
    db.drop_all()
    db.create_all()
    return "✅ قاعدة البيانات أُعيد تعيينها بدون الحاجة لتسجيل الدخول (للتطوير فقط)."
