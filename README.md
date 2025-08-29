# User Surveillance System

A smart surveillance system with user and police interfaces, WhatsApp alert integration, and password management. Built with Flask, Streamlit, Twilio, AWS S3, and SQLite.

## Features
- User registration, login, and persistent sessions
- Password reset (Forgot Password)
- Detection model activation/deactivation
- WhatsApp alerts with image (via AWS S3)
- Police alert and call integration

## Project Structure
```
Surveillance-System-main/
│
├── backend/
│   ├── app.py                # Flask backend (API)
│   ├── model.py              # Detection model logic
│   ├── police_alert.py       # WhatsApp/Twilio/AWS S3 integration
│   ├── database.db           # User database (SQLite)
│   ├── police_database.db    # Police database (SQLite)
│   └── requirements.txt      # Backend dependencies
│
├── user_app.py               # Streamlit frontend for users
├── police_app.py             # Streamlit frontend for police
└── README.md                 # Project documentation
```

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <repo-url>
cd Surveillance-System-main
```

### 2. Install Backend Dependencies
```sh
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
- Set your Twilio, AWS S3, and other credentials in `police_alert.py`.

### 4. Run the Backend (Flask API)
```sh
cd backend
python app.py
```

### 5. Run the User Frontend (Streamlit)
```sh
cd ..
streamlit run user_app.py
```

### 6. Run the Police Frontend (Streamlit)
```sh
streamlit run police_app.py
```

## Usage
- Register as a user and log in.
- Activate detection to receive WhatsApp alerts with images if movement is detected.
- Respond to WhatsApp alerts with `OK` or `NOT OK`.
- Use "Forgot Password" if you need to reset your password.
- Police can log in and receive alerts/calls as configured.

## Notes
- Make sure your Twilio sandbox is set up for WhatsApp and your AWS S3 bucket allows public read for images.
- All sensitive credentials should be kept secure and not hardcoded in production.

## License
MIT License
