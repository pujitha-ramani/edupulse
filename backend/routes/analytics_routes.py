from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Event, Registration, Feedback
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    if user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    total_events = Event.query.count()
    total_users = User.query.count()
    total_regs = Registration.query.filter_by(status='confirmed').count()
    certs = Registration.query.filter_by(certificate_issued=True).count()

    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating else 0.0

    return jsonify({
        'total_events': total_events,
        'total_users': total_users,
        'total_registrations': total_regs,
        'certificates_issued': certs,
        'average_rating': avg_rating,
    }), 200


@analytics_bp.route('/participation-trend', methods=['GET'])
@jwt_required()
def participation_trend():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    if user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    result = []
    for i in range(7, -1, -1):
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=30 * i))
        month_end = (datetime.utcnow().replace(day=1) - timedelta(days=30 * (i - 1))) if i > 0 else datetime.utcnow()
        count = Registration.query.filter(
            Registration.registered_at >= month_start,
            Registration.registered_at < month_end,
            Registration.status == 'confirmed'
        ).count()
        result.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    return jsonify(result), 200


@analytics_bp.route('/category-breakdown', methods=['GET'])
@jwt_required()
def category_breakdown():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    if user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    rows = db.session.query(Event.category, func.count(Event.id)).group_by(Event.category).all()
    return jsonify([{'category': r[0], 'count': r[1]} for r in rows]), 200


@analytics_bp.route('/rating-distribution', methods=['GET'])
@jwt_required()
def rating_distribution():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    if user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    rows = db.session.query(Feedback.rating, func.count(Feedback.id)).group_by(Feedback.rating).all()
    dist = {str(i): 0 for i in range(1, 6)}
    for rating, count in rows:
        dist[str(rating)] = count
    return jsonify(dist), 200
