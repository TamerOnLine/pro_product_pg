# routes/auth_utils.py

from functools import wraps
from flask import session, redirect, url_for, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_auth.login'))
        return f(*args, **kwargs)
    return decorated_function



def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return render_template('errors/unauthorized.html'), 403
        return f(*args, **kwargs)
    return decorated_function

