from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Event, User, Registration
from datetime import datetime

event_bp = Blueprint('events', __name__)


def require_role(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            uid = get_jwt_identity()
            user = User.query.get(uid)
            if not user or user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


@event_bp.route('/', methods=['GET'])
@jwt_required()
def get_events():
    user_id = get_jwt_identity()
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'date')

    query = Event.query.filter(Event.status != 'cancelled')
    if category and category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            db.or_(
                Event.title.ilike(f'%{search}%'),
                Event.description.ilike(f'%{search}%'),
                Event.tags.ilike(f'%{search}%'),
                Event.organizer.ilike(f'%{search}%')
            )
        )
    if sort == 'date':
        query = query.order_by(Event.date.asc())
    elif sort == 'name':
        query = query.order_by(Event.title.asc())

    events = query.all()
    if sort == 'seats':
        events.sort(key=lambda e: e.seats - e.registered_count, reverse=True)

    return jsonify([e.to_dict(user_id=user_id) for e in events]), 200


@event_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    user_id = get_jwt_identity()
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict(user_id=user_id)), 200


@event_bp.route('/', methods=['POST'])
@require_role('organizer', 'admin')
def create_event():
    user_id = get_jwt_identity()
    data = request.get_json()

    required = ['title', 'category', 'date', 'venue', 'seats', 'organizer']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    cat_emojis = {
        'Technical': '💻', 'Cultural': '🎭', 'Sports': '⚽',
        'Workshop': '🛠️', 'Seminar': '🎤'
    }
    try:
        event_date = datetime.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601'}), 400

    event = Event(
        title=data['title'].strip(),
        category=data['category'],
        description=data.get('description', ''),
        date=event_date,
        venue=data['venue'].strip(),
        seats=int(data['seats']),
        organizer=data['organizer'].strip(),
        deadline=datetime.fromisoformat(data['deadline']).date() if data.get('deadline') else None,
        tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', ''),
        emoji=cat_emojis.get(data['category'], '📅'),
        status='upcoming',
        created_by=user_id
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event created', 'event': event.to_dict()}), 201


@event_bp.route('/<int:event_id>', methods=['PUT'])
@require_role('organizer', 'admin')
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    for field in ['title', 'category', 'description', 'venue', 'organizer', 'status']:
        if field in data:
            setattr(event, field, data[field])
    if 'seats' in data:
        event.seats = int(data['seats'])
    if 'date' in data:
        event.date = datetime.fromisoformat(data['date'])
    if 'deadline' in data and data['deadline']:
        event.deadline = datetime.fromisoformat(data['deadline']).date()
    if 'tags' in data:
        event.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    db.session.commit()
    return jsonify({'message': 'Event updated', 'event': event.to_dict()}), 200


@event_bp.route('/<int:event_id>', methods=['DELETE'])
@require_role('organizer', 'admin')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200


@event_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    interests = user.interests.split(',') if user.interests else []

    registered_ids = [r.event_id for r in Registration.query.filter_by(user_id=user_id).all()]
    events = Event.query.filter(
        Event.category.in_(interests),
        ~Event.id.in_(registered_ids),
        Event.status == 'upcoming'
    ).order_by(Event.date.asc()).limit(10).all()

    return jsonify([e.to_dict(user_id=user_id) for e in events]), 200
