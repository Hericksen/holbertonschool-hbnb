# app/models/user.py

import bcrypt
from app.models.base_model import BaseModel
import re
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class User(BaseModel):
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.validate_email()
        self.hash_password(password)

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Email non valide")

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __str__(self):
        return f"User({self.id}, {self.first_name} {self.last_name}, {self.email})"

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)
