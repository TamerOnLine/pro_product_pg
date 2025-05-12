from models.models_definitions import db, Notification
from logic.notifications import create_notification

def hide_old_notifications(product_id, role, type):
    """
    إخفاء جميع الإشعارات السابقة المرتبطة بمهمة واحدة
    """
    Notification.query.filter_by(
        product_id=product_id,
        role=role,
        type=type,
        is_visible=True
    ).update({'is_visible': False})
    db.session.commit()

def push_next_notification(user_id, role, message, type, product_id):
    """
    إنشاء إشعار جديد للمرحلة التالية في المهمة
    """
    create_notification(
        user_id=user_id,
        role=role,
        message=message,
        type=type,
        product_id=product_id,
        is_visible=True
    )


def advance_notification(
    product_id,
    from_role,
    from_type,
    to_user_id,
    to_role,
    to_type,
    message
):
    """
    تحريك الإشعار من مرحلة إلى أخرى:
    - إخفاء الإشعارات القديمة المرتبطة بالمُرسِل
    - إرسال إشعار جديد للمُستقبِل

    Args:
        product_id (int): معرف المنتج المرتبط بالمهمة
        from_role (str): الدور الذي نُخفي إشعاراته القديمة
        from_type (str): نوع الإشعار القديم
        to_user_id (int or None): لمن نرسل الإشعار الجديد
        to_role (str): دوره
        to_type (str): نوع الإشعار الجديد
        message (str): نص الإشعار
    """
    hide_old_notifications(product_id, from_role, from_type)

    push_next_notification(
        user_id=to_user_id,
        role=to_role,
        message=message,
        type=to_type,
        product_id=product_id
    )
