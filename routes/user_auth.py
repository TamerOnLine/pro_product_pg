from flask import Blueprint, request, session, current_app, render_template, redirect, url_for, flash
from models.models_definitions import db, User
from logic.notification_service import create_notification, get_user_notifications
from logic.validation_utils import validate_form


user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('products.index'))


@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()

        # Define validation schema
        schema = {
            'email': {
                'type': 'string',
                'regex': r'^[^@]+@[^@]+\.[^@]+$',
                'required': True
            },
            'username': {
                'type': 'string',
                'minlength': 3,
                'maxlength': 30,
                'required': True
            },
            'password': {
                'type': 'string',
                'minlength': 8,
                'required': True
            },
            'role': {
                'type': 'string',
                'allowed': ['admin', 'merchant', 'customer'],
                'required': False
            }
        }

        # Validate the form data
        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])
        if not is_valid:
            flash("There were errors in your registration form.", "error")
            return render_template('auth/register.html', errors=result)

        # Check if the user already exists
        existing_user = User.query.filter(
            (User.email == result['email']) | (User.username == result['username'])
        ).first()

        if existing_user:
            flash("Email or username already in use.", "error")
            return render_template('auth/register.html', errors={
                'username': ['Email or username already in use.']
            })

        # Create the user and hash the password
        user = User(
            email=result['email'],
            username=result['username'],
            role=result.get('role', 'customer')
        )
        user.set_password(result['password'])  # Hash the password before saving
        db.session.add(user)
        db.session.commit()

        flash(f"Welcome {user.username}, you have successfully registered!", "success")
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

        if user and user.check_password(password):  # Verify password
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash("Successfully logged in!", "success")

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'merchant':
                return redirect(url_for('merchant.dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('user_auth.dashboard'))

            return redirect(url_for('products.index'))

        flash("Invalid login credentials. Please try again.", "error")
        return render_template('auth/login.html', error="Invalid login credentials")

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
    flash("You have been logged out.", "info")
    return redirect(url_for('user_auth.login'))


@user_auth_bp.route('/profile')
def profile():
    """Display the current user's profile."""
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)


@user_auth_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    """Allow the user to edit their profile."""
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        data = request.form.to_dict()

        # Validation schema
        schema = {
            'email': {
                'type': 'string',
                'regex': r'^[^@]+@[^@]+\.[^@]+$',
                'required': True
            },
            'username': {
                'type': 'string',
                'minlength': 3,
                'maxlength': 30,
                'required': True
            }
        }

        # Validate the data
        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])

        if not is_valid:
            flash("There were errors in updating your profile.", "error")
            return render_template('auth/edit_profile.html', user=user, errors=result)

        # Update user data
        user.username = result['username']
        user.email = result['email']
        db.session.commit()

        flash("Your profile has been updated successfully.", "success")
        return redirect(url_for('user_auth.profile'))

    return render_template('auth/edit_profile.html', user=user)


@user_auth_bp.route('/delete_account', methods=['POST'])
def delete_account():
    """Allow the user to delete their account."""
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Your account has been deleted.", "warning")
    return redirect(url_for('user_auth.register'))  # Redirect to register page or login
