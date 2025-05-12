# logic/validation_utils.py

import re

from cerberus import Validator
import bleach

def sanitize_text_fields(data, fields):
    for field in fields:
        if field in data:
            data[field] = bleach.clean(data[field])
    return data

def validate_form(data, schema, sanitize_fields=None):
    if sanitize_fields:
        data = sanitize_text_fields(data, sanitize_fields)
    v = Validator(schema)
    if not v.validate(data):
        return False, v.errors
    return True, v.document


def validate_email(email):
    """تحقق من صحة صيغة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def validate_password(password, min_length=8):
    """تحقق من طول كلمة المرور"""
    return len(password) >= min_length

def sanitize_text(text):
    """تعقيم النص لمنع هجمات XSS"""
    return bleach.clean(text)

def validate_price(price):
    """التحقق من أن السعر رقم موجب"""
    try:
        value = float(price)
        return value >= 0
    except ValueError:
        return False
