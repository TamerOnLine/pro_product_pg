from flask import Blueprint, request, render_template, redirect, url_for, session
from models.models_definitions import db, User
from logic.notifications import create_notification, get_user_notifications
from logic.validation_utils import validate_form



user_auth_bp = Blueprint('user_auth', __name__)


@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()

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

        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])

        if not is_valid:
            return render_template('auth/register.html', errors=result)

        # التحقق من عدم وجود المستخدم مسبقًا
        existing_user = User.query.filter(
            (User.email == result['email']) | (User.username == result['username'])
        ).first()

        if existing_user:
            return render_template('auth/register.html', errors={
                'username': ['Email or username already in use.']
            })

        # إنشاء المستخدم
        user = User(
            email=result['email'],
            username=result['username'],
            role=result.get('role', 'customer')
        )
        user.set_password(result['password'])
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

        return render_template('auth/login.html', error="بيانات الدخول غير صحيحة")


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


@user_auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)


@user_auth_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        data = request.form.to_dict()

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

        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])

        if not is_valid:
            return render_template('auth/edit_profile.html', user=user, errors=result)



        user.username = result['username']
        user.email = result['email']
        db.session.commit()
        return redirect(url_for('user_auth.profile'))

    return render_template('auth/edit_profile.html', user=user)


@user_auth_bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('user_auth.login'))

    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return redirect(url_for('user_auth.register'))  # أو login

