"""Persistent prediction history using SQLAlchemy."""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    filename = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(40), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_name = db.Column(db.String(120), nullable=False)
    ai_probability = db.Column(db.Float, nullable=False)
