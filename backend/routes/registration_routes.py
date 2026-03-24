from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, mail
from models import Registration, Event, User, Notification
from flask_mail import Message
from datetime import datetime

reg_bp = Blueprint('registrations', __name__)


def send_confirmation_email(user, event):
    try:
        msg = Message(
            subject=f'Registration Confirmed: {event.title}',
            recipients=[user.email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
              <div style="background:#e8440a;padding:20px;border-radius:12px 12px 0 0;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:28px;">EduPulse 🎓</h1>
              </div>
              <div style="background:#fff;padding:30px;border:1px solid #eee;border-radius:0 0 12px 12px;">
                <h2 style="color:#1a1814;">Registration Confirmed! ✅</h2>
                <p>Hi <strong>{user.name}</strong>,</p>
                <p>You have successfully registered for:</p>
                <div style="background:#f7f6f3;padding:16px;border-radius:8px;margin:16px 0;border-left:4px solid #e8440a;">
                  <h3 style="margin:0 0 8px;color:#e8440a;">{event.emoji} {event.title}</h3>
                  <p style="margin:4px 0;color:#5a5650;">📅 {event.date.strftime('%B %d, %Y at %I:%M %p')}</p>
                  <p style="margin:4px 0;color:#5a5650;">📍 {event.venue}</p>
                  <p style="margin:4px 0;color:#5a5650;">🏫 {event.organizer}</p>
                </div>
                <p style="color:#5a5650;">Please arrive 10 minutes early. Bring your student ID.</p>
                <p style="color:#8a8680;font-size:12px;margin-top:24px;">— EduPulse Team</p>
              </div>
            </div>
            """
        )
        mail.send(msg)
    except Exception:
        pass  # Don't fail registration if email fails


@reg_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_registrations():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    query = Registration.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    regs = query.order_by(Registration.registered_at.desc()).all()
    result = []
    for r in regs:
        d = r.to_dict()
        d['event'] = r.event.to_dict() if r.event else None
        result.append(d)
    return jsonify(result), 200


@reg_bp.route('/', methods=['POST'])
@jwt_required()
def register_event():
    user_id = get_jwt_identity()
    data = request.get_json()
    event_id = data.get('event_id')

    if not event_id:
        return jsonify({'error': 'event_id is required'}), 400

    event = Event.query.get_or_404(event_id)
    user = User.query.get_or_404(user_id)

    existing = Registration.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return jsonify({'error': 'Already registered or waitlisted for this event'}), 409

    is_full = event.registered_count >= event.seats
    status = 'waitlist' if is_full else 'confirmed'

    reg = Registration(user_id=user_id, event_id=event_id, status=status)
    db.session.add(reg)

    # Notification
    notif = Notification(
        user_id=user_id,
        title='Registration Confirmed ✅' if status == 'confirmed' else 'Added to Waitlist ⏳',
        description=f'Your {"registration" if status=="confirmed" else "waitlist entry"} for {event.title} is saved.',
        icon='✅' if status == 'confirmed' else '⏳'
    )
    db.session.add(notif)
    db.session.commit()

    if status == 'confirmed':
        send_confirmation_email(user, event)

    return jsonify({
        'message': f'Successfully {"registered" if status=="confirmed" else "added to waitlist"}',
        'registration': reg.to_dict(),
        'status': status
    }), 201


@reg_bp.route('/<int:reg_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(reg_id):
    user_id = get_jwt_identity()
    reg = Registration.query.get_or_404(reg_id)

    if reg.user_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role not in ('admin',):
            return jsonify({'error': 'Unauthorized'}), 403

    event_title = reg.event.title if reg.event else 'the event'
    db.session.delete(reg)

    # Promote waitlisted user if a confirmed seat opens up
    if reg.status == 'confirmed':
        next_wait = Registration.query.filter_by(
            event_id=reg.event_id, status='waitlist'
        ).order_by(Registration.registered_at.asc()).first()
        if next_wait:
            next_wait.status = 'confirmed'
            notif = Notification(
                user_id=next_wait.user_id,
                title='You got a spot! 🎉',
                description=f'A seat opened up for {event_title}. Your registration is now confirmed!',
                icon='🎉'
            )
            db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Registration cancelled'}), 200


@reg_bp.route('/<int:reg_id>/certificate', methods=['POST'])
@jwt_required()
def issue_certificate(reg_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    reg = Registration.query.get_or_404(reg_id)

    # Only admin/organizer can issue, or self-issue after event
    if reg.user_id != user_id and user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    reg.certificate_issued = True
    db.session.commit()

    notif = Notification(
        user_id=reg.user_id,
        title='Certificate Ready 🏆',
        description=f'Your certificate for {reg.event.title} is ready to download!',
        icon='🏆'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Certificate issued', 'registration': reg.to_dict()}), 200


@reg_bp.route('/event/<int:event_id>/attendees', methods=['GET'])
@jwt_required()
def get_attendees(event_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if user.role not in ('admin', 'organizer'):
        return jsonify({'error': 'Unauthorized'}), 403

    regs = Registration.query.filter_by(event_id=event_id).all()
    result = []
    for r in regs:
        d = r.to_dict()
        d['user'] = r.user.to_dict(include_email=True) if r.user else None
        result.append(d)
    return jsonify(result), 200
