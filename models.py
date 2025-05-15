from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    infos = db.relationship('Info', backref='user', cascade="all, delete-orphan")
    sessions = db.relationship('Session', backref = 'user', cascade = 'all, delete-orphan')

class Info(db.Model):
    __tablename__ = 'info'
    info_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    position = db.Column(db.String(500), nullable=False)
    interest = db.Column(db.String(500), nullable=False)
    history = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(500), nullable=False)
    project = db.Column(db.String(500), nullable=False)
    resume = db.Column(db.String(5000))

    sessions = db.relationship('Session', backref='info', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='info', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='info', cascade='all, delete-orphan')

class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info_id = db.Column(db.Integer, db.ForeignKey('info.info_id'), unique=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    messages = db.relationship('Message', backref='session', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='session', cascade='all, delete-orphan')

class Sender(Enum):
    user = 'user'
    system = 'system'

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.message_id', ondelete='SET NULL'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id', ondelete='CASCADE'), nullable=True)
    info_id = db.Column(db.Integer, db.ForeignKey('info.info_id'), nullable = False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    sender = db.Column(db.Enum(Sender), nullable=True)
    content = db.Column(db.String(5000))
    role = db.Column(db.String(100))
    temperature = db.Column(db.Float)
    max_token = db.Column(db.Integer)
    quality = db.Column(db.Integer)

    # 명시적으로 primaryjoin 조건 설정
    replies = db.relationship(
        'Message',
        backref=db.backref('parent', remote_side=[message_id]),
        primaryjoin="Message.parent_id == Message.message_id",
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    
class Report(db.Model):
    __tablename__ = 'report'
    report_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    info_id = db.Column(db.Integer, db.ForeignKey('info.info_id'), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expression = db.Column(db.String(500), nullable=False)
    weak = db.Column(db.String(500), nullable=False)
    fix = db.Column(db.String(500), nullable=False)
    score = db.Column(db.Integer, nullable=False)