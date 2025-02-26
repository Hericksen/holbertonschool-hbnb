# app/models/user.py

from base_model import BaseModel
import re

class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.validate_email()

    def validate_email(self):
        """Valide l'email pour s'assurer qu'il est au format correct"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Email non valide")

    def __str__(self):
        return f"User({self.id}, {self.first_name} {self.last_name}, {self.email})"
