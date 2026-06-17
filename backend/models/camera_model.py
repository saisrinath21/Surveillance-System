from extensions.extensions import db


class Camera(db.Model):
    __tablename__ = 'cameras'
    camera_id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    camera_name = db.Column(db.String(100), nullable=False)
    camera_url = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.String(200), nullable=False)
    longitude = db.Column(db.String(200), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    model_active = db.Column(db.Boolean, default=False)