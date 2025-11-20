# ==========================
# models.py
# ==========================

from datetime import datetime, date, timedelta
import random
import string

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


# ---------------------- GENERADOR DE ID ----------------------
def generar_id_numerico(longitud=8):
    return ''.join(random.choices(string.digits, k=longitud))


# ---------------------- MODELO USER ----------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # ID visible del cliente (solo números)
    client_id = db.Column(db.String(16), unique=True, nullable=False, index=True)

    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscription_date = db.Column(db.Date, nullable=True)
    subscription_days = db.Column(db.Integer, nullable=True)

    routines = db.relationship('Routine', backref='user', lazy=True, cascade='all,delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not getattr(self, 'client_id', None):
            nuevo_id = generar_id_numerico(8)
            while User.query.filter_by(client_id=nuevo_id).first():
                nuevo_id = generar_id_numerico(8)
            self.client_id = nuevo_id

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password_plaintext):
        self.password_hash = generate_password_hash(password_plaintext)

    def check_password(self, password_plaintext):
        return check_password_hash(self.password_hash, password_plaintext)

    def is_admin(self):
        return self.role == 'admin'

    def days_remaining(self):
        if not self.subscription_date or not self.subscription_days:
            return None
        try:
            start = self.subscription_date
            if isinstance(start, datetime):
                start = start.date()
            end_date = start + timedelta(days=self.subscription_days)
            remaining = (end_date - date.today()).days
            return remaining if remaining > 0 else 0
        except:
            return None


# ---------------------- MODELO ROUTINE ----------------------
class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creado_por = db.Column(db.String(150), nullable=True)

    exercises = db.relationship('Exercise', backref='routine', lazy=True, cascade='all,delete-orphan')


# ---------------------- MODELO EXERCISE ----------------------
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    series = db.Column(db.Integer, nullable=True)
    repeticiones = db.Column(db.String(50), nullable=True)
    peso = db.Column(db.String(50), nullable=True)
    dia = db.Column(db.String(30), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    rutina_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
