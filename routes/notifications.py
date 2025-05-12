from flask import Blueprint, session, request, render_template, redirect, url_for, abort
from models.models_definitions import db, Notification
from logic.notifications import get_user_notifications

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
def show_notifications():
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')

    notifications = get_user_notifications(role, user_id)
    unread_count = sum(1 for n in notifications if not n.is_read)

    return render_template(
        'shared/notifications.html',
        notifications=notifications,
        unread_count=unread_count
    )


@notifications_bp.route('/notifications/<int:note_id>/hide', methods=['POST'])
def hide_notification(note_id):
    note = Notification.query.get_or_404(note_id)
    role = session.get('role')
    user_id = session.get('user_id')

    if note.role != role or (note.user_id and note.user_id != user_id):
        abort(403)

    note.is_visible = False
    db.session.commit()
    return redirect(url_for('notifications.show_notifications'))


@notifications_bp.route('/notifications/<int:note_id>/restore', methods=['POST'])
def restore_notification(note_id):
    note = Notification.query.get_or_404(note_id)
    role = session.get('role')
    user_id = session.get('user_id')

    if note.role != role or (note.user_id and note.user_id != user_id):
        abort(403)

    note.is_visible = True
    db.session.commit()
    return redirect(url_for('notifications.notification_archive'))


@notifications_bp.route('/notifications/archive')
def notification_archive():
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')

    notifications = Notification.query.filter_by(role=role, is_visible=False)

    if user_id:
        notifications = notifications.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
    else:
        notifications = notifications.filter_by(user_id=None)

    notifications = notifications.order_by(Notification.created_at.desc()).all()

    return render_template('shared/notifications_archive.html', notifications=notifications)
