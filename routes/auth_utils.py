from functools import wraps
from flask import session, redirect, url_for, render_template

def login_required(f):
    """
    Decorator that ensures a user is logged in before accessing the route.

    Args:
        f (function): The route function to wrap.

    Returns:
        function: The wrapped function that redirects to login if the user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_auth.login'))
        return f(*args, **kwargs)

    return decorated_function

def admin_only(f):
    """
    Decorator that restricts access to admin users only.

    Args:
        f (function): The route function to wrap.

    Returns:
        function: The wrapped function that returns a 403 error page if the user is not an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return render_template('errors/unauthorized.html'), 403
        return f(*args, **kwargs)

    return decorated_function
