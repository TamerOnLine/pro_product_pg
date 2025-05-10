# routes/merchant.py

from flask import Blueprint, render_template, session
from routes.auth_utils import login_required

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')

@merchant_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'merchant':
        return render_template("errors/unauthorized.html"), 403
    return render_template('merchant/dashboard.html', username=session['username'])
