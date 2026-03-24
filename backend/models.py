from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student | organizer | admin
    interests = db.Column(db.Text, default='')          # comma-separated
    status = db.Column(db.String(20), default='active') # active | inactive | banned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='user', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_email=False):
        d = {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'interests': self.interests.split(',') if self.interests else [],
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'registrations_count': len(self.registrations),
        }
        if include_email:
            d['email'] = self.email
        return d


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)   # Technical|Cultural|Sports|Workshop|Seminar
    description = db.Column(db.Text, default='')
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    seats = db.Column(db.Integer, nullable=False, default=100)
    organizer = db.Column(db.String(150), nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    tags = db.Column(db.Text, default='')                 # comma-separated
    emoji = db.Column(db.String(10), default='📅')
    status = db.Column(db.String(20), default='upcoming') # upcoming|ongoing|completed|cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def registered_count(self):
        return Registration.query.filter_by(event_id=self.id, status='confirmed').count()

    def to_dict(self, user_id=None):
        d = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat(),
            'venue': self.venue,
            'seats': self.seats,
            'registered': self.registered_count,
            'organizer': self.organizer,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'tags': self.tags.split(',') if self.tags else [],
            'emoji': self.emoji,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
        if user_id:
            reg = Registration.query.filter_by(event_id=self.id, user_id=user_id).first()
            d['user_registration'] = reg.to_dict() if reg else None
        return d


class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed|waitlist|cancelled
    certificate_issued = db.Column(db.Boolean, default=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_user_event'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'status': self.status,
            'certificate_issued': self.certificate_issued,
            'registered_at': self.registered_at.isoformat(),
        }


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)   # 1-5
    comment = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_feedback_user_event'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else '',
            'event_id': self.event_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    icon = db.Column(db.String(10), default='🔔')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
        }
