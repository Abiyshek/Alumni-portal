"""
SQLAlchemy Database Models for Alumni ML Platform
Defines schemas for User, Alumni, Engagement, and Donation data
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and RBAC"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagements = db.relationship('Engagement', backref='recorded_by_user', lazy='dynamic', foreign_keys='Engagement.recorded_by_id')
    donations = db.relationship('Donation', backref='recorded_by_user', lazy='dynamic', foreign_keys='Donation.recorded_by_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Alumni(db.Model):
    """Alumni model for storing alumni profiles and scores"""
    __tablename__ = 'alumni'
    
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    graduation_year = db.Column(db.Integer)
    department = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    current_position = db.Column(db.String(255))
    current_company = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(500))
    
    # Scoring
    engagement_score = db.Column(db.Float, default=0.0)
    donation_score = db.Column(db.Float, default=0.0)
    engagement_level = db.Column(db.String(50), default='low')  # 'low', 'medium', 'high'
    last_engagement = db.Column(db.DateTime)
    
    # Aggregated data
    total_donations = db.Column(db.Float, default=0.0)
    donation_count = db.Column(db.Integer, default=0)
    engagement_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagements = db.relationship('Engagement', backref='alumni_obj', lazy='dynamic', cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='alumni_obj', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_history=False):
        """Convert to dictionary"""
        data = {
            'alumni_id': self.id,
            'name': self.name,
            'email': self.email,
            'graduation_year': self.graduation_year,
            'department': self.department,
            'phone': self.phone,
            'current_position': self.current_position,
            'current_company': self.current_company,
            'linkedin_url': self.linkedin_url,
            'engagement_score': round(self.engagement_score, 3),
            'donation_score': round(self.donation_score, 3),
            'engagement_level': self.engagement_level,
            'last_engagement': self.last_engagement.isoformat() if self.last_engagement else None,
            'total_donations': self.total_donations,
            'donation_count': self.donation_count,
            'engagement_count': self.engagement_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_history:
            data['engagement_events'] = [e.event_type for e in self.engagements.all()]
            data['latest_donation'] = self.donations.order_by(Donation.date.desc()).first().to_dict() if self.donations.first() else None
        
        return data
    
    def update_scores(self):
        """Recalculate engagement and donation scores"""
        # Engagement score based on recent activity
        recent_engagements = self.engagements.filter(
            Engagement.date >= datetime.utcnow().replace(day=1).replace(month=1)
        ).count()
        self.engagement_score = min(1.0, recent_engagements / 10.0)
        
        # Donation score based on total donations
        if self.total_donations > 0:
            # Normalize: 0-1000 = 0.0-1.0
            self.donation_score = min(1.0, self.total_donations / 10000.0)
        
        # Engagement level
        if self.engagement_score >= 0.7:
            self.engagement_level = 'high'
        elif self.engagement_score >= 0.4:
            self.engagement_level = 'medium'
        else:
            self.engagement_level = 'low'
    
    def __repr__(self):
        return f'<Alumni {self.id}: {self.name}>'


class Engagement(db.Model):
    """Engagement model for tracking alumni interactions"""
    __tablename__ = 'engagements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alumni_id = db.Column(db.String(100), db.ForeignKey('alumni.id'), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)  # 'attendance', 'newsletter', 'login', 'email', etc.
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    recorded_by_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata
    source = db.Column(db.String(100))  # 'web', 'email', 'phone', 'api', etc.
    metadata_json = db.Column(db.JSON)  # Additional custom data
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alumni_id': self.alumni_id,
            'event_type': self.event_type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'recorded_by': self.recorded_by_id,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'source': self.source,
            'metadata_json': self.metadata_json
        }
    
    def __repr__(self):
        return f'<Engagement {self.alumni_id}: {self.event_type}>'


class Donation(db.Model):
    """Donation model for tracking alumni donations"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alumni_id = db.Column(db.String(100), db.ForeignKey('alumni.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    fund_type = db.Column(db.String(100), nullable=False)  # 'general', 'scholarship', 'infrastructure', 'research', etc.
    currency = db.Column(db.String(10), default='USD')
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    recorded_by_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Transaction info
    payment_method = db.Column(db.String(100))  # 'credit_card', 'bank_transfer', 'check', 'cash', etc.
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    reference_id = db.Column(db.String(255), unique=True, nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='completed')  # 'pending', 'completed', 'failed', 'refunded'
    notes = db.Column(db.Text)
    
    # Metadata
    metadata_json = db.Column(db.JSON)  # Additional custom data
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alumni_id': self.alumni_id,
            'amount': self.amount,
            'fund_type': self.fund_type,
            'currency': self.currency,
            'date': self.date.isoformat() if self.date else None,
            'recorded_by': self.recorded_by_id,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'reference_id': self.reference_id,
            'status': self.status,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Donation {self.id}: {self.alumni_id} - ${self.amount}>'


class AuditLog(db.Model):
    """Audit log model for tracking all system activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(100))  # 'alumni', 'engagement', 'donation', 'user', etc.
    resource_id = db.Column(db.String(255))
    status = db.Column(db.String(50))  # 'success', 'failure'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(50))
    details = db.Column(db.JSON)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'details': self.details
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'
