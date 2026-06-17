# Surveillance System

A smart surveillance platform with separate user and police web applications, real-time alert delivery, camera monitoring, OTP support, AWS S3 image upload, Twilio call and WhatsApp notification support, and a Flask backend.

## Features

- User registration, login, and profile management
- Police login and alert handling dashboard
- OTP verification and authentication flows
- Camera registration and detection control
- Real-time alert updates using Socket.IO
- Police dispatch and call user support
- AWS S3 image storage for alert snapshots
- Twilio notifications for calls and WhatsApp
- SQLAlchemy ORM with MySQL/SQLite compatibility

## Repository Structure

```
Surveillance-System/
├── backend/                 # Flask backend and API services
│   ├── app.py               # Flask application factory
│   ├── run.py               # Backend startup script using Flask-SocketIO
│   ├── config/              # Configuration and environment utilities
│   ├── extensions/          # Flask extensions (db, socketio, cors, etc.)
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API blueprints and endpoints
│   ├── services/            # Twilio, AWS, police, detection logic
│   ├── utils/               # JWT helpers, phone utils, district utils
│   └── yolov8n.pt           # Detection model weights
├── frontend/                # React/Vite frontend applications
│   ├── admin-app/           # Admin interface (if configured)
│   ├── police-app/          # Police alert dashboard
│   └── user-app/            # User-facing interface
├── requirements.txt         # Python backend dependencies
└── README.md                # Project documentation
```

## Prerequisites

- Python 3.10+ (recommended)
- Node.js 18+ and npm
- AWS account and S3 bucket for image uploads
- Twilio account for phone/WhatsApp alerts
- Optional: MySQL database, or SQLite for local development

## Backend Setup

1. Clone the repository:

```sh
git clone <repo-url>
cd Surveillance-System
```

2. Create and activate a Python virtual environment:

```sh
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install backend dependencies:

```sh
pip install -r requirements.txt
```

4. Create a `.env` file in the repository root with required environment variables:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///backend.db
FRONTEND_BASE_URL=http://localhost:5173
ACCOUNT_SID=your-twilio-account-sid
AUTH_TOKEN=your-twilio-auth-token
FROM_NUMBER=whatsapp:+14155238886
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-s3-bucket-name
AWS_S3_REGION=your-aws-region
```

5. Start the backend:

```sh
cd backend
python run.py
```

The backend serves on `http://localhost:8080`.

## Frontend Setup

### User app

```sh
cd frontend/user-app
npm install
npm run dev
```

### Police app

```sh
cd frontend/police-app
npm install
npm run dev
```

Both frontends use Vite in development mode.

## Useful Commands

```sh
# Backend
cd backend
python run.py

# User frontend
cd frontend/user-app
npm run dev

# Police frontend
cd frontend/police-app
npm run dev
```

## Important Notes

- The police dashboard uses Socket.IO to receive real-time alert updates.
- Alerts are considered resolved only when police explicitly set status to `resolved`.
- New escalated alerts from user actions should appear in police history and update stats via sockets.
- AWS S3 must be configured for image uploads and public access.
- Twilio credentials must be valid for calls and WhatsApp integration.

## Backend Overview

- `backend/app.py` — creates Flask app and registers blueprints
- `backend/run.py` — starts the Flask-SocketIO server and initializes the database
- `backend/routes/` — API endpoints for alerts, auth, profile, and police workflows
- `backend/services/` — integrations for Twilio, AWS, police search, and detection
- `backend/models/` — user, alert, camera, police, and related ORM models

## Frontend Overview

- `frontend/user-app/` — user-facing React app for alerts and camera management
- `frontend/police-app/` — police dashboard for alert handling, calling, and resolution

## Troubleshooting

- If the frontend cannot connect, verify the backend is running at `http://localhost:8080`
- Confirm `FRONTEND_BASE_URL` and backend CORS configuration
- If Twilio fails, verify `ACCOUNT_SID`, `AUTH_TOKEN`, and `FROM_NUMBER`
- If image uploads fail, verify AWS S3 credentials, bucket, and permissions

## License

MIT License
