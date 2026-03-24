from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Feedback, Registration, Notification

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_feedback():
    uid = get_jwt_identity()
    fb = Feedback.query.filter_by(user_id=uid).all()
    return jsonify([f.to_dict() for f in fb]), 200


@feedback_bp.route('/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_feedback(event_id):
    fb = Feedback.query.filter_by(event_id=event_id).all()
    return jsonify([f.to_dict() for f in fb]), 200


@feedback_bp.route('/', methods=['POST'])
@jwt_required()
def submit_feedback():
    uid = get_jwt_identity()
    data = request.get_json()
    event_id = data.get('event_id')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not event_id or not rating:
        return jsonify({'error': 'event_id and rating are required'}), 400
    if not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    reg = Registration.query.filter_by(user_id=uid, event_id=event_id).first()
    if not reg:
        return jsonify({'error': 'You must be registered for this event to leave feedback'}), 403

    existing = Feedback.query.filter_by(user_id=uid, event_id=event_id).first()
    if existing:
        existing.rating = int(rating)
        existing.comment = comment
        db.session.commit()
        return jsonify({'message': 'Feedback updated', 'feedback': existing.to_dict()}), 200

    fb = Feedback(user_id=uid, event_id=event_id, rating=int(rating), comment=comment)
    db.session.add(fb)
    db.session.commit()
    return jsonify({'message': 'Feedback submitted', 'feedback': fb.to_dict()}), 201
