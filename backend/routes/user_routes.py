from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    uid = get_jwt_identity()
    me = User.query.get_or_404(uid)
    if me.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    users = User.query.all()
    return jsonify([u.to_dict(include_email=True) for u in users]), 200


@user_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_status(user_id):
    uid = get_jwt_identity()
    me = User.query.get_or_404(uid)
    if me.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.status = data.get('status', user.status)
    db.session.commit()
    return jsonify({'message': 'Status updated', 'user': user.to_dict(include_email=True)}), 200
