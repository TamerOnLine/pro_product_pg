import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask
from models.models_definitions import db
from myapp  import app  # عدّل هذا حسب اسم مشروعك الحقيقي

with app.app_context():
    # 1. استخراج أسماء الجداول
    tables = db.metadata.tables.keys()
    tables = list(tables)

    # 2. عرض قائمة مرقمة
    print("📋 الجداول الحالية:")
    print("0) حذف كل الجداول")
    for i, table_name in enumerate(tables, start=1):
        print(f"{i}) {table_name}")

    # 3. طلب الاختيار
    choice = input("أدخل رقم الجدول الذي تريد حذفه (أو 0 لحذف الكل): ").strip()

    try:
        choice = int(choice)
        if choice == 0:
            confirm = input("⚠️ تأكيد: هل تريد حذف كل الجداول؟ (y/n): ")
            if confirm.lower() == 'y':
                db.drop_all()
                print("✅ تم حذف جميع الجداول.")
        elif 1 <= choice <= len(tables):
            table_name = tables[choice - 1]
            db.metadata.tables[table_name].drop(db.engine)
            print(f"✅ تم حذف الجدول: {table_name}")
        else:
            print("❌ اختيار غير صالح.")
    except Exception as e:
        print(f"❌ خطأ: {e}")
