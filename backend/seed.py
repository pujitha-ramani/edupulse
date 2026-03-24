from app import db, bcrypt
from models import User, Event, Registration, Notification, Feedback
from datetime import datetime, timedelta
import random


def seed_database():
    """Seed the database with sample data — runs only once."""
    if User.query.first():
        return  # Already seeded

    print("🌱 Seeding database...")

    # ── Users ─────────────────────────────────────────────────
    users_data = [
        ('Alex Johnson',    'alex@college.edu',    'student',   'password123', 'Technical,Workshop'),
        ('Dr. Sarah Chen',  'sarah@college.edu',   'organizer', 'org123',      'Technical,Seminar'),
        ('Prof. Mike Ray',  'admin@college.edu',   'admin',     'admin123',    'Cultural,Sports'),
        ('Priya Sharma',    'priya@college.edu',   'student',   'pass123',     'Cultural,Sports'),
        ('Rajan Mehta',     'rajan@college.edu',   'student',   'pass123',     'Technical,Workshop,Seminar'),
        ('Anjali Nair',     'anjali@college.edu',  'student',   'pass123',     'Cultural,Seminar'),
        ('Dev Patel',       'dev@college.edu',     'organizer', 'pass123',     'Sports,Technical'),
    ]
    users = []
    for name, email, role, pw, interests in users_data:
        u = User(
            name=name, email=email, role=role,
            password_hash=bcrypt.generate_password_hash(pw).decode('utf-8'),
            interests=interests
        )
        db.session.add(u)
        users.append(u)
    db.session.flush()

    # ── Events ────────────────────────────────────────────────
    now = datetime.utcnow()
    events_data = [
        ('National Hackathon 2025',        'Technical', now+timedelta(days=5),   'CS Lab Complex',        100, 78,  'CS Department',    'Coding competition with ₹2L prize pool. 36-hour team hackathon solving real-world AI problems.', 'coding,AI,team',                '💻'),
        ('Spring Cultural Festival',       'Cultural',  now+timedelta(days=12),  'Open Air Theatre',      500, 320, 'Cultural Committee','Celebrate diversity — music, dance, food and art from across India and the world.',              'dance,music,food',              '🎭'),
        ('Inter-College Football Cup',     'Sports',    now+timedelta(days=18),  'Sports Ground',         22,  22,  'Sports Council',   'Compete against 10 colleges in this prestigious tournament. Group stages through Finals.',        'football,tournament',           '⚽'),
        ('Machine Learning Workshop',      'Workshop',  now+timedelta(days=22),  'Seminar Hall B',        60,  45,  'AI Club',          'Hands-on workshop covering supervised learning, neural networks, and deployment with TensorFlow.', 'ML,Python,AI,deep-learning',   '🧠'),
        ('TEDx Campus Talks',              'Seminar',   now+timedelta(days=30),  'Main Auditorium',       300, 210, 'TEDx Team',        'Ideas worth spreading — inspiring speakers changing the world in unexpected ways.',               'inspiration,talks,leadership',  '🎤'),
        ('Web Dev Bootcamp',               'Workshop',  now+timedelta(days=35),  'Innovation Lab',        40,  18,  'WebDev Club',      'Learn modern web development from scratch — HTML, CSS, JavaScript, React and Node.js.',           'web,react,javascript',          '🌐'),
        ('Photography Exhibition',         'Cultural',  now+timedelta(days=40),  'Art Gallery',           200, 85,  'Photo Club',       'Curated student photography exploring identity, nature and urban life themes.',                   'art,photography',               '📷'),
        ('Entrepreneurship Summit',        'Seminar',   now+timedelta(days=45),  'Conference Center',     150, 130, 'E-Cell',           'Connect with founders, investors, and mentors. Pitch your startup for seed funding!',            'startup,business,pitch',        '🚀'),
        ('Annual Sports Day',              'Sports',    now+timedelta(days=51),  'Sports Complex',        400, 156, 'Sports Council',   'Compete in athletics, swimming, badminton and more. Represent your department!',                  'athletics,sports,annual',       '🏅'),
        ('Open Mic Night',                 'Cultural',  now+timedelta(days=55),  'Student Center',        120, 42,  'Arts Council',     'Open stage for poetry, standup, music, spoken word. Sign up to perform or just vibe!',           'music,comedy,poetry',           '🎸'),
        ('Robotics Championship',          'Technical', now+timedelta(days=62),  'Engineering Block',     80,  65,  'Robotics Club',    'Design and battle your robot: maze solving, sumo, and autonomous navigation categories.',         'robotics,engineering',          '🤖'),
        ('Mental Health Seminar',          'Seminar',   now+timedelta(days=70),  'Health Center Hall',    200, 55,  'Student Welfare',  'Expert panel on stress management, academic pressure and resilience. Open to all.',              'wellness,mental-health',        '🧘'),
    ]
    events = []
    for title, cat, date, venue, seats, reg_count, org, desc, tags, emoji in events_data:
        e = Event(
            title=title, category=cat, date=date, venue=venue,
            seats=seats, organizer=org, description=desc,
            tags=tags, emoji=emoji, status='upcoming',
            deadline=(date - timedelta(days=5)).date(),
            created_by=users[1].id
        )
        db.session.add(e)
        events.append(e)
    db.session.flush()

    # ── Registrations for Alex (user 0) ──────────────────────
    alex = users[0]
    reg_events = [events[0], events[3], events[7], events[10]]
    reg_statuses = ['confirmed', 'confirmed', 'confirmed', 'waitlist']
    cert_flags = [True, False, True, False]
    for ev, status, cert in zip(reg_events, reg_statuses, cert_flags):
        r = Registration(user_id=alex.id, event_id=ev.id, status=status, certificate_issued=cert)
        db.session.add(r)

    # ── Registrations for other students ─────────────────────
    for ev in events[:8]:
        for u in users[3:6]:
            if random.random() > 0.4:
                r = Registration(user_id=u.id, event_id=ev.id, status='confirmed')
                db.session.add(r)

    db.session.flush()

    # ── Feedback ──────────────────────────────────────────────
    fb1 = Feedback(user_id=alex.id, event_id=events[0].id, rating=5,
                   comment='Fantastic event! Challenges were well-designed and the team was super supportive.')
    fb2 = Feedback(user_id=alex.id, event_id=events[7].id, rating=4,
                   comment='Great speakers and networking. Would love longer Q&A next time.')
    db.session.add_all([fb1, fb2])

    # ── Notifications for Alex ────────────────────────────────
    notifs = [
        Notification(user_id=alex.id, title='Registration Confirmed ✅', description='Your spot for National Hackathon 2025 is confirmed!', icon='✅', is_read=False),
        Notification(user_id=alex.id, title='Event Reminder 🔔', description='Machine Learning Workshop starts in 3 days. Bring your laptop!', icon='🔔', is_read=False),
        Notification(user_id=alex.id, title='New Event Added 🆕', description='Mental Health Seminar has been added. Check it out!', icon='🆕', is_read=False),
        Notification(user_id=alex.id, title='Certificate Ready 🏆', description='Your certificate for Entrepreneurship Summit is ready to download.', icon='🏆', is_read=True),
        Notification(user_id=alex.id, title='Feedback Requested ⭐', description='Please rate the events you attended last week.', icon='⭐', is_read=True),
        Notification(user_id=alex.id, title='Welcome to EduPulse! 🎉', description='Start exploring events and register for ones you love.', icon='🎉', is_read=True),
    ]
    db.session.add_all(notifs)
    db.session.commit()
    print("✅ Database seeded successfully!")
