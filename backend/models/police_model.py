from extensions.extensions import db

class Police(db.Model):
    __tablename__ = 'police'
    id = db.Column(db.String(30), primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.String(200), nullable=False)
    longitude = db.Column(db.String(200), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
