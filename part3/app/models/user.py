# app/models/user.py

from flask_bcrypt import Bcrypt
from app.models.base_model import BaseModel
import re

bcrypt = Bcrypt()


class User(BaseModel):
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
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
