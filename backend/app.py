from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import timedelta
import sqlite3
import model
import police_alert
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable cross-origin session support
app.secret_key = 'your_secret_key'  # Required for session management
app.permanent_session_lifetime = timedelta(days=7)  # Optional: make session last 7 days


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
    con.commit()
    con.close()

    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS police (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        password TEXT,
        address TEXT,
        phone TEXT UNIQUE
    )''')
    con.commit()
    con.close()


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


@app.route('/police-register', methods=['POST'])
def police_register():
    data = request.json
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO police (code, password, address, phone)
                       VALUES (?, ?, ?, ?)''',
                    (data['code'], data['password'], data['address'], data['phone']))
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

@app.route('/incoming-whatsapp', methods=['POST'])
def incoming_whatsapp():
    from_number = request.form.get('From')
    incoming_msg = request.form.get('Body', '').strip().upper()

    response = MessagingResponse()
    raw_number = from_number.replace('whatsapp:', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT address, phone FROM users WHERE phone = ?", (raw_number,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        response.message("User not recognized.")
        return str(response)

    user_address, user_phone = result

    if incoming_msg == "NOT OK":
        police_alert.call_police(user_address, user_phone)
        response.message("Police have been notified.")
    elif incoming_msg == "OK":
        response.message("Glad to hear you're safe. Monitoring will continue.")
    else:
        response.message("Please reply with 'OK' or 'NOT OK'.")

    return str(response)


@app.route('/send-alert', methods=['POST'])
def send_alert():
    data = request.json
    image_path = data.get("image_path")
    whatsapp_number = data.get("whatsapp_number")
    if not image_path or not whatsapp_number:
        return jsonify({"error": "Missing image_path or whatsapp_number"}), 400
    return police_alert.alert_user_via_whatsapp(image_path, whatsapp_number)


@app.route('/call-police', methods=['POST'])
def call_police_route():
    data = request.json
    user_address = data.get("user_address")
    user_phone_number = data.get("user_phone_number")
    if not user_address or not user_phone_number:
        return jsonify({"error": "Missing user_address or user_phone_number"}), 400
    return police_alert.call_police(user_address, user_phone_number)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
