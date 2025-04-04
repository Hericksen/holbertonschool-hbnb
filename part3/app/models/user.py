# app/models/user.py

from flask_bcrypt import Bcrypt
from app.models.base_model import BaseModel
import re

bcrypt = Bcrypt()


class User(BaseModel):
    """
    User class.
    Attributes:
      - id (inherited from BaseModel)
      - first_name, last_name: Required, maximum 50 characters.
      - email: Required, must be unique and in a valid format.
      - is_admin: Boolean (default: False)
      - password: Hashed password (not exposed in GET responses)
      - places: List of owned Places.
      - reviews: List of written Reviews.
    """
    __tablename__ = 'users'


"""
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reviews = db.relationship('Review', backref='user',
                              lazy=True, cascade='all, delete')

    existing_emails = set()
"""


def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError(
                "Invalid first_name (must be non-empty and ≤ 50 characters).")
        if not last_name or len(last_name) > 50:
            raise ValueError(
                "Invalid last_name (must be non-empty and ≤ 50 characters).")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")
        if email in User.existing_emails:
            raise ValueError("This email is already in use.")
        User.existing_emails.add(email)

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hash_password(password)
        self.is_admin = is_admin
        self.validate_email()

def validate_email(self):
        """Valide l'email pour s'assurer qu'il est au format correct"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Email non valide")

def hash_password(self, password):
        """Hash le mot de passe avec bcrypt"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(self, password):
        """Vérifie si le mot de passe est correct"""
        return bcrypt.check_password_hash(self.password, password)

def __str__(self):
        return f"User({self.id}, {self.first_name} {self.last_name}, {self.email})"
