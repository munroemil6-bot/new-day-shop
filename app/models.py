from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()

MIN_PASSWORD_LENGTH = 4


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    purchases = db.relationship('Purchase', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.')
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email,}


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    purchases = db.relationship('Purchase', back_populates='item', cascade='all, delete-orphan')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'price': self.price, 'stock': self.stock,}


class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    purchased_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='purchases')
    item = db.relationship('Item', back_populates='purchases')

    def to_dict(self):
        return {'id': self.id, 'quantity': self.quantity, 'total_price': self.total_price, 'purchased_at': self.purchased_at.isoformat(), 'item': self.item.to_dict() if self.item else None, 'user': {
                'id': self.user.id, 'username': self.user.username,
            },
        }
