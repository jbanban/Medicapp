from flask import jsonify
from flask_login import login_required, current_user
from app.models import Notification
from app.models import Patient
from app import db

from . import patient_bp

# ── Get notifications (used in navbar) ──────────────────────────────
@patient_bp.route('/notifications')
@login_required
def get_notifications():

    patient = Patient.query.filter_by(patient_id=current_user.user_id).first()

    notifications = Notification.query.filter_by(
        patient_id=patient.patient_id
    ).order_by(Notification.created_at.desc()).limit(10).all()

    return jsonify([{
        'notification_id' : n.notification_id,
        'title'           : n.title,
        'message'         : n.message,
        'type'            : n.type,
        'is_read'         : n.is_read,
        'created_at'      : n.created_at.strftime('%b %d, %I:%M %p')
    } for n in notifications])


# ── Mark single notification as read ────────────────────────────────
@patient_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):

    patient = Patient.query.filter_by(patient_id=current_user.user_id).first()

    notif = Notification.query.filter_by(
        notification_id=notification_id,
        patient_id=patient.patient_id
    ).first_or_404()

    notif.is_read = True
    db.session.commit()

    return jsonify({'success': True})


# ── Mark all notifications as read ──────────────────────────────────
@patient_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    
    patient = Patient.query.filter_by(patient_id=current_user.user_id).first()

    Notification.query.filter_by(
        patient_id=patient.patient_id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()

    return jsonify({'success': True})


# ── Helper: create a notification (call this from other routes) ──────
def create_notification(patient_id, title, message, type='general'):
    notif = Notification(
        patient_id=patient_id,
        title=title,
        message=message,
        type=type
    )
    db.session.add(notif)
    db.session.commit()
    return notif