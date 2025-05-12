from flask import Blueprint
from models.models_definitions import db
from routes.auth_utils import admin_only

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/admin/reset_db', methods=['POST'])
@admin_only
def reset_db():
    db.drop_all()
    db.create_all()
    return "All tables have been dropped and recreated.", 200




@reset_bp.route('/dev/reset')
def dev_reset():
    """
    Drops all tables and recreates them without authentication.
    Intended for development use only.

    Returns:
        tuple: A success message and HTTP status code 200.
    """
    db.drop_all()
    db.create_all()
    return "Database has been reset (development mode).", 200
