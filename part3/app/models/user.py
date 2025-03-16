import re
from app import db, bcrypt
from app.models.BaseModel import BaseModel


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

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete')

    existing_emails = set()

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
        self.is_admin = is_admin

        self.hash_password(password)

    def hash_password(self, password):
        """Hash the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verify the provided password against the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """Return a dictionary representation of the user (excluding the password)."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "places": [p.id for p in self.places],
            "reviews": [r.id for r in self.reviews]
        }
