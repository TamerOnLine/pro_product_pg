from functools import wraps
from flask import session, redirect, url_for, render_template, abort
from logic.notifications import create_notification, get_user_notifications


from flask import session, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            abort(401)  # بدلاً من redirect
        return f(*args, **kwargs)
    return decorated_function





def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
