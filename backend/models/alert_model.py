from extensions.extensions import db
from datetime import datetime
from sqlalchemy.orm import synonym

class Alert(db.Model):
    __tablename__ = 'alerts'
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    alert_id = db.Column(db.String(36), primary_key=True)
    camera_id = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    user_response = db.Column(db.String(20))
    police_station_id = db.Column('police_called', db.String(36), db.ForeignKey('police.id'), nullable=True)
    police_called = synonym('police_station_id')
