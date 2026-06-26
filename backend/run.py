from app import create_app
from extensions.extensions import db, socketio

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=8080, debug=True, use_reloader=False)
