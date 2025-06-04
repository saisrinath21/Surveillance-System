# --- Updated app.py ---
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import model
import police_alert
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # Required for session management

def init_db():
    # Initialize user database
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

    # Initialize police database
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
    data = request.json
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO users (username, password, address, phone)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (data['username'], data['password'], data['address'], data['phone']))
        con.commit()
        return jsonify({'message': 'Registered'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User exists'}), 409
    finally:
        con.close()

@app.route('/police-register', methods=['POST'])
def police_register():
    data = request.json
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO police (code, password, address, phone)
                       VALUES (?, ?, ?, ?, ?)''',
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
        session['username'] = user[1]
        session['id'] = user[0] 
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/activate', methods=['GET'])
def activate():
    username = session.get('username')
    user_id = session.get('id')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    model.start_detection(user_id)
    return jsonify({'message': f'Model Activated for {username}'})

@app.route('/deactivate', methods=['GET'])
def deactivate():
    model.stop_detection()
    return jsonify({'message': 'Model Deactivated'})

@app.route('/incoming-whatsapp', methods=['POST'])
def incoming_whatsapp():
    from_number = request.form.get('From')  # Format: whatsapp:+91XXXXXXXXXX
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)