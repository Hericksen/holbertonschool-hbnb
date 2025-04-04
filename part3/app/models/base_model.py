from app import db
import uuid
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True  # This ensures SQLAlchemy does not create a table for BaseModel

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    """
    Base class that provides:
      - Unique ID (UUID)
      - Timestamps (created_at, updated_at)
      - Methods to update attributes and timestamps
    """

    def save(self):
        """Update the 'updated_at' timestamp when the object is modified."""
        self.updated_at = datetime.now()

    def update(self, data: dict):
        """
        Update object attributes from a dictionary.
        Also updates the 'updated_at' timestamp.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
