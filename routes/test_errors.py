import os
from flask import Blueprint, abort, render_template, current_app

test_errors_bp = Blueprint('test_errors', __name__, url_prefix='/test-errors')

def is_dev_mode():
    return current_app.config.get("ENV") == "development"

@test_errors_bp.before_request
def block_if_not_dev():
    if not is_dev_mode():
        abort(403)

@test_errors_bp.route('/401')
def trigger_401():
    abort(401)

@test_errors_bp.route('/403')
def trigger_403():
    abort(403)

@test_errors_bp.route('/404')
def trigger_404():
    abort(404)

@test_errors_bp.route('/500')
def trigger_500():
    raise Exception("🔥 اختبار خطأ داخلي")

@test_errors_bp.route('/custom/<int:code>')
def trigger_custom(code):
    abort(code)
