from base_model import BaseModel
import re


class User(BaseModel):
    """Représente un utilisateur."""

    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()
        self.first_name = self.validate_name(first_name)
        self.last_name = self.validate_name(last_name)
        self.email = self.validate_email(email)
        self.is_admin = is_admin

    def validate_name(self, name):
        if len(name) > 50:
            raise ValueError(
                "Le prénom et le nom ne peuvent pas dépasser 50 caractères.")
        return name

    def validate_email(self, email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            raise ValueError("Email invalide.")
        return email
