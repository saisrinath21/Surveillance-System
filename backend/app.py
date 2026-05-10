from turtle import st

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import timedelta
import sqlite3
import model
import police_alert
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('secret_key')
app.permanent_session_lifetime = timedelta(days=7) 


def init_db():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        address TEXT,
        phone TEXT UNIQUE
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        image_url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        user_response TEXT,
        police_called INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    con.commit()
    con.close()

    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS police (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        password TEXT,
        address TEXT,
        district TEXT,
        phone TEXT UNIQUE
    )''')
    con.commit()
    con.close()

# Forgot Password endpoint
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')
    new_password = data.get('new_password')
    if not username or not phone or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE username=? AND phone=?', (username, phone))
    user = cur.fetchone()
    if not user:
        con.close()
        return jsonify({'error': 'User not found or phone number does not match'}), 404
    cur.execute('UPDATE users SET password=? WHERE username=? AND phone=?', (new_password, username, phone))
    con.commit()
    con.close()
    return jsonify({'message': 'Password reset successful'}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'password', 'address', 'phone']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400

    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('''
            INSERT INTO users (username, password, address, phone)
            VALUES (?, ?, ?, ?)
        ''', (data['username'], data['password'], data['address'], data['phone']))
        con.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User already exists'}), 409
    finally:
        con.close()

    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE username=? AND password=?', (data['username'], data['password']))
    user = cur.fetchone()
    con.close()
    if user:
        session.permanent = True
        session['username'] = user[1]
        session['id'] = user[0]
        print('Session contents after login:', dict(session))
        return jsonify({'message': 'Login successful'}), 200

    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/police-register', methods=['POST'])
def police_register():
    data = request.json
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO police (code, password, address, district, phone)
                       VALUES (?, ?, ?, ?, ?)''',
                    (data['code'], data['password'], data['address'], data.get('district', ''), data['phone']))
        con.commit()
        return jsonify({'message': 'Police Registered'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Police code/phone already exists'}), 409
    finally:
        con.close()


@app.route('/police-login', methods=['POST'])
def police_login():
    data = request.json
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM police WHERE code=? AND password=?', (data['code'], data['password']))
    user = cur.fetchone()
    con.close()
    if user:
        session.permanent = True
        session['police_code'] = user[1]
        session['police_id'] = user[0]
        return jsonify({'message': 'Police Login successful'})
    else:
        return jsonify({'error': 'Invalid police credentials'}), 401


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/activate', methods=['GET'])
def activate():
    username = session.get('username')
    user_id = session.get('id')

    if not username or not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    print('Session contents at activate:', dict(session))
    try:
        model.start_detection(user_id)
        return jsonify({'message': f'Model Activated for {username}'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to activate model: {str(e)}'}), 500


@app.route('/deactivate', methods=['GET'])
def deactivate():
    try:
        model.stop_detection()
        return jsonify({'message': 'Model Deactivated'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to deactivate model: {str(e)}'}), 500

@app.route('/incoming-whatsapp?', methods=['GET', 'POST'])
def incoming_whatsapp():
    from_number = request.form.get('From')
    incoming_msg = request.form.get('Body')
    response = MessagingResponse()
    raw_number = from_number.replace('whatsapp:', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, address, district, phone FROM users WHERE phone = ?", (raw_number,))
    result = cursor.fetchone()
    
    if not result:
        cursor.close()
        conn.close()
        return  "User not recognized.", 400

    user_id, user_address, user_district, user_phone = result
    try:
        if incoming_msg == "OK":
            cursor.execute('''UPDATE alerts 
                            SET status='resolved', user_response=? 
                            WHERE user_id=? AND status='pending' 
                            ORDER BY timestamp DESC LIMIT 1''', (incoming_msg, user_id))
            conn.commit()
  
        if incoming_msg == "NOT OK":
            cursor.execute('''UPDATE alerts 
                            SET status='resolved', user_response=?, police_called=1 
                            WHERE user_id=? AND status='pending' 
                            ORDER BY timestamp DESC LIMIT 1''', (incoming_msg, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            police_alert.call_police(user_address, user_district, user_phone)
            return "Response processed successfully.", 200
    except Exception as e:
        cursor.close()
        conn.close()
        return f"Error processing your response: {str(e)}", 400


@app.route('/get-alerts', methods=['GET'])
def get_alerts():
    """Fetch all alerts for the logged-in user"""
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    
    limit = request.args.get('limit', 20, type=int)
    
    try:
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('''SELECT id, image_url, timestamp, status, user_response, police_called 
                      FROM alerts 
                      WHERE user_id = ? 
                      ORDER BY timestamp DESC 
                      LIMIT ?''', (user_id, limit))
        alerts = [dict(row) for row in cur.fetchall()]
        con.close()
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/call-police', methods=['POST'])
def call_police_route():
    data = request.json
    user_address = data.get("user_address")
    user_phone_number = data.get("user_phone_number")
    if not user_address or not user_phone_number:
        return jsonify({"error": "Missing user_address or user_phone_number"}), 400
    return police_alert.call_police(user_address, user_phone_number)


if __name__ == "__main__":
    app.run(debug=True)