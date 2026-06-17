from extensions.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(30), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)