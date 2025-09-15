from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to diary entries
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def mark_email_verified(self):
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'

class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationship to user
    user = db.relationship('User', backref='verification_codes')
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired()
    
    def mark_used(self):
        self.used = True
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    @staticmethod
    def create_for_user(user_id, expires_in_minutes=15):
        """Create a new verification code for a user"""
        code = VerificationCode.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        # Invalidate any existing codes for this user
        VerificationCode.query.filter_by(user_id=user_id, used=False).update({'used': True})
        
        return VerificationCode(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.JSON)  # Store all question answers as JSON
    summary = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    advice = db.Column(db.Text)
    
    def __repr__(self):
        return f'<DiaryEntry {self.id} for User {self.user_id}>'
