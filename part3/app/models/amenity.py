from app import db
from app.models.BaseModel import BaseModel


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref='amenities', lazy=True)

    def __init__(self, name, owner_id=None):
        super().__init__()

        if not name or len(name) > 50:
            raise ValueError(
                "Invalid 'name': must be non-empty and ≤ 50 characters.")

        self.name = name
        self.owner_id = owner_id
