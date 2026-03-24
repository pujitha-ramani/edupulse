# 🎓 EduPulse — College Event Dashboard

A full-stack, production-ready college event management platform built with **Flask** (backend) and **Vanilla JS + HTML/CSS** (frontend).

---

## 🏗️ Project Structure

```
edupulse/
├── backend/
│   ├── app.py                  # Flask app factory & server entry point
│   ├── models.py               # SQLAlchemy database models
│   ├── seed.py                 # Database seeder with sample data
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   └── routes/
│       ├── auth_routes.py      # Login, Register, JWT refresh
│       ├── event_routes.py     # CRUD for events + recommendations
│       ├── registration_routes.py  # Register, cancel, waitlist, certificates
│       ├── user_routes.py      # User management (Admin)
│       ├── analytics_routes.py # Dashboard analytics & charts data
│       ├── feedback_routes.py  # Event ratings & reviews
│       └── notification_routes.py  # Notifications management
├── frontend/
│   └── index.html              # Full SPA frontend (connects to Flask API)
└── README.md
```

---

## ⚙️ Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Backend   | Python 3.10+, Flask 3.x                 |
| Database  | SQLite (dev) / MySQL or PostgreSQL (prod)|
| Auth      | JWT (Flask-JWT-Extended) + Bcrypt       |
| ORM       | SQLAlchemy                              |
| Email     | Flask-Mail (SMTP)                       |
| CORS      | Flask-CORS                              |
| Frontend  | Vanilla HTML/CSS/JS (no framework)      |
| Charts    | Chart.js 4.x                            |
| PDF       | jsPDF                                   |
| AI Chat   | Anthropic Claude API                    |
| Fonts     | Google Fonts (Syne + DM Sans)           |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- pip

### 2. Clone / Extract the project
```bash
cd edupulse
```

### 3. Set up Python environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your values (SECRET_KEY, JWT_SECRET_KEY, etc.)
```

### 5. Run the server
```bash
python app.py
```

The server starts at **http://localhost:5000**

The database is **automatically created and seeded** with sample data on first run.

---

## 🔑 Demo Accounts

| Role      | Email                   | Password      |
|-----------|-------------------------|---------------|
| 👑 Admin    | admin@college.edu       | admin123      |
| 🎯 Organizer | sarah@college.edu      | org123        |
| 🎓 Student  | alex@college.edu        | password123   |
| 🎓 Student  | priya@college.edu       | pass123       |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| POST   | /api/auth/register    | Create new account     |
| POST   | /api/auth/login       | Login, returns JWT     |
| POST   | /api/auth/refresh     | Refresh access token   |
| GET    | /api/auth/me          | Get current user       |
| PUT    | /api/auth/me          | Update profile         |

### Events
| Method | Endpoint                   | Description                  |
|--------|----------------------------|------------------------------|
| GET    | /api/events/               | List all events (filterable) |
| GET    | /api/events/:id            | Get single event             |
| POST   | /api/events/               | Create event (Org/Admin)     |
| PUT    | /api/events/:id            | Update event (Org/Admin)     |
| DELETE | /api/events/:id            | Delete event (Org/Admin)     |
| GET    | /api/events/recommendations| Personalized recommendations |

### Registrations
| Method | Endpoint                              | Description             |
|--------|---------------------------------------|-------------------------|
| GET    | /api/registrations/                   | My registrations        |
| POST   | /api/registrations/                   | Register for event      |
| DELETE | /api/registrations/:id                | Cancel registration     |
| POST   | /api/registrations/:id/certificate    | Issue certificate       |
| GET    | /api/registrations/event/:id/attendees| List attendees (Org)    |

### Analytics (Organizer/Admin only)
| Method | Endpoint                              | Description             |
|--------|---------------------------------------|-------------------------|
| GET    | /api/analytics/summary                | Overall stats           |
| GET    | /api/analytics/participation-trend    | Monthly trend data      |
| GET    | /api/analytics/category-breakdown     | Events by category      |
| GET    | /api/analytics/rating-distribution    | Rating histogram        |

### Other
| Method | Endpoint                        | Description          |
|--------|---------------------------------|----------------------|
| GET    | /api/feedback/                  | My feedback          |
| POST   | /api/feedback/                  | Submit feedback      |
| GET    | /api/notifications/             | My notifications     |
| PUT    | /api/notifications/:id/read     | Mark one as read     |
| PUT    | /api/notifications/read-all     | Mark all as read     |
| GET    | /api/users/                     | All users (Admin)    |
| PUT    | /api/users/:id/status           | Update status (Admin)|

---

## 🌟 Features

### Authentication & Roles
- JWT-based authentication with refresh tokens
- Three roles: **Student**, **Organizer**, **Admin**
- Role-based UI — nav items and actions appear based on your role
- Auto-login via stored token

### Event Management
- 12 pre-seeded events across 5 categories
- Create, edit, delete events (Organizer/Admin)
- Category filtering, name/date/seats sorting, full-text search
- Real-time seat tracking with visual progress bars

### Registration System
- One-click registration with confirmation modal
- Automatic **waitlist** when event is full
- Waitlist promotion — when a confirmed user cancels, the next waitlisted user is auto-promoted
- Email confirmation (configure SMTP in .env)

### Certificates
- Issue PDF certificates via jsPDF
- Custom branded design with event details
- Download directly from browser

### AI Chatbot (PulseBot)
- Powered by Anthropic Claude API
- Context-aware — knows current user and events
- Graceful fallback responses when API is unavailable

### Analytics (Charts)
- Participation trend (line chart)
- Events by category (doughnut chart)  
- Monthly activity (bar chart)
- Rating distribution (horizontal bar)

### Notifications
- Auto-created on registration, certificate issuance, waitlist updates
- Unread count badge in sidebar
- Mark individual or all as read

---

## 🔧 Production Deployment

### Switch to PostgreSQL/MySQL
```bash
# In .env:
DATABASE_URL=postgresql://user:password@localhost/edupulse
# or
DATABASE_URL=mysql+pymysql://user:password@localhost/edupulse
```

### Use Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Use Nginx as reverse proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location / { proxy_pass http://127.0.0.1:5000; }
}
```

---

## 📧 Email Setup

For real confirmation emails, configure Gmail App Password:

1. Enable 2FA on your Gmail account
2. Generate an App Password at myaccount.google.com/apppasswords
3. Set in `.env`:
```
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
```

---

## 🛠️ Development Notes

- Database resets on deletion of `instance/edupulse.db` — just restart to re-seed
- Frontend uses `fetch` to call `/api/...` endpoints (same-origin, no CORS needed in prod)
- All API routes require JWT except `/api/auth/login` and `/api/auth/register`
- Charts load from real analytics API endpoints when on the Analytics page

---

*Built with ❤️ using Flask + Vanilla JS*
