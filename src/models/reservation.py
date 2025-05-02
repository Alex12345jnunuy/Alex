from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True) # Email might be optional depending on channel
    reservation_date = db.Column(db.Date, nullable=False)
    reservation_time = db.Column(db.Time, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='confirmed', nullable=False) # e.g., confirmed, cancelled
    channel = db.Column(db.String(20), nullable=False) # e.g., 'web', 'whatsapp'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.id} for {self.customer_name} on {self.reservation_date} at {self.reservation_time}>'

