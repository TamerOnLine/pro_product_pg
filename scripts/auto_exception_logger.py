import os
import re

PROJECT_DIR = "."  # غيرها إذا حبيت تحدد مسار آخر

pattern = re.compile(r"except Exception as e:\n(\s*)print\((.*?)\)\n(\s*)return (.*?)")

replacement = (
    "except Exception as e:\n"
    "\1current_app.logger.exception(\"\u274C حدث استثناء أثناء تنفيذ العملية\")\n"
    "\3return \"حدث خطأ غير متوقع. الرجاء المحاولة لاحقًا.\", 500"
)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    new_content = pattern.sub(replacement, content)

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"✅ تم تعديل: {filepath}")


def scan_project():
    for root, dirs, files in os.walk(PROJECT_DIR):
        for filename in files:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                process_file(full_path)

if __name__ == "__main__":
    scan_project()
