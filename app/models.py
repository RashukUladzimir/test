from app import db, login
from flask_login import UserMixin

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(11))
    name = db.Column(db.String(64))
    auth_hash = db.Column(db.String(128))
    client_id = db.Column(db.Integer)
    text_storage = db.Column(db.String(1024), default='{}')
    step = db.Column(db.Integer, default=0)
    tg_id = db.Column(db.Integer, unique=True)
    records = db.relationship('Record', backref='user', lazy='dynamic')

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer)
    record_hash = db.Column(db.String(128))
    services = db.Column(db.String(256))
    service_ids = db.Column(db.String(128))
    date = db.Column(db.String(64))
    company_id = db.Column(db.Integer)
    master_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))
    password = db.Column(db.String(16))

@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))