from flask import Blueprint, request, render_template, redirect, url_for, session
from models.models_definitions import db, User  # تأكد من استخدام الاسم الجديد إذا غيّرت models.py

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return "🚫 البريد الإلكتروني أو اسم المستخدم مستخدم بالفعل."

        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_auth.login'))

    return render_template('auth/register.html')


@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect('/')

        return "❌ بيانات الدخول غير صحيحة."

    return render_template('auth/login.html')


@user_auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_auth.login'))
