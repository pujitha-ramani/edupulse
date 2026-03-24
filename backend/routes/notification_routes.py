from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Notification

notif_bp = Blueprint('notifications', __name__)


@notif_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    uid = get_jwt_identity()
    notifs = Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifs]), 200


@notif_bp.route('/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notif_id):
    uid = get_jwt_identity()
    n = Notification.query.get_or_404(notif_id)
    if n.user_id != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    n.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200


@notif_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    uid = get_jwt_identity()
    Notification.query.filter_by(user_id=uid, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200


@notif_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    uid = get_jwt_identity()
    count = Notification.query.filter_by(user_id=uid, is_read=False).count()
    return jsonify({'count': count}), 200
