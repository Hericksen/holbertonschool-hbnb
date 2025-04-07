#!/user/bin/python3
'''create class user'''


import re
import uuid
from app.models.basemodel import BaseModel
from app import db, bcrypt


class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete')

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = self.validate_first_name(first_name)
        self.last_name = self.validate_last_name(last_name)
        self.email = self.validate_email(email)
        self.is_admin = is_admin
        self.hash_password(password)

    def validate_first_name(self, first_name):
        if not first_name or len(first_name) > 50:
            raise ValueError("First name must be non-empty and less than or equal to 50 characters.")
        return first_name

    def validate_last_name(self, last_name):
        if not last_name or len(last_name) > 50:
            raise ValueError("Last name must be non-empty and less than or equal to 50 characters.")
        return last_name

    def validate_email(self, email):
        # Basic email validation using a regular expression
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError("Email must be in a valid format.")
        # Assuming we would check for email uniqueness in a larger system
        return email

    def add_place(self, place):
        from app.models.place import Place
        if not isinstance(place, Place):
            raise TypeError("The place does not exist")
        self.places.append(place)

    def list_places(self):
        for x in self.places:
            print(f"{x}")

    def __str__(self):
        return f"User({self.id}, {self.first_name} {self.last_name}, {self.email}, Admin: {self.is_admin}, Created at: {self.created_at}, Last updated: {self.updated_at})"

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        if len(self.password) == 60 and self.password.startswith('$2b$'):
            return True
        return False

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
