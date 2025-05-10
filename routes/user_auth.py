from flask import Blueprint, request, render_template, redirect, url_for, session
from models.models_definitions import db, User

user_auth_bp = Blueprint('user_auth', __name__)


@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration by accepting form input for email, username, 
    password, and role. Stores the new user in the database if no duplicate exists.

    Returns:
        Response: Redirects to login page upon success or renders the registration page.
    """
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'customer')

        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            return "Email or username already in use."

        user = User(email=email, username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_auth.login'))

    return render_template('auth/register.html')


@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login by verifying email/username and password.
    Sets user session upon successful login and redirects based on role.

    Returns:
        Response: Redirects to role-based dashboard or renders login page.
    """
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'merchant':
                return redirect(url_for('merchant.dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('user_auth.dashboard'))

            return redirect(url_for('products.index'))

        return "Invalid login credentials."

    return render_template('auth/login.html')


@user_auth_bp.route('/dashboard')
def dashboard():
    """
    Display the user dashboard if the user is logged in.

    Returns:
        Response: Renders the dashboard template or redirects to login.
    """
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    return render_template('auth/dashboard.html', username=session['username'])


@user_auth_bp.route('/logout')
def logout():
    """
    Clear the current session and redirect to the login page.

    Returns:
        Response: Redirects to login page.
    """
    session.clear()
    return redirect(url_for('user_auth.login'))
