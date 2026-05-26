from extensions.extensions import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = 'alerts'
    alert_id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('users.id'), nullable=False)
    # camera_url = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    user_response = db.Column(db.String(20))
    police_called = db.Column(db.Boolean, default=False)

