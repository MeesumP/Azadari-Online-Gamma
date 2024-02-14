from . import db
from sqlalchemy.sql import func
from sqlalchemy import JSON

class Lyric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), unique=True)
    type = db.Column(JSON, nullable=False)
    link = db.Column(db.String(1000), nullable=True, default="")
    linkTime = db.Column(db.String(50), nullable=True, default="")
    words = db.Column(db.String(100000000000000), unique=True)
    pace = db.Column(db.String(5), default="")
    hands = db.Column(JSON, nullable=True, default=[])
    topics = db.Column(JSON, nullable=False)

class toAdd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    words = db.Column(db.String(1000000000))