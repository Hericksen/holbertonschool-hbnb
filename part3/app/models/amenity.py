#!/user/bin/python3


from app.models.basemodel import BaseModel
from app import db

class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref='amenities', lazy=True)

    def __init__(self, name):
        super().__init__()
        self.name = self.validate_name(name)

    def validate_name(self, name):
        if not name:
            raise ValueError("Amenity name must be provided.")
        if len(name) > 50:
            raise ValueError("Amenity name must be less than or equal to 50 characters.")
        return name

    def __str__(self):
        return (f"Amenity({self.id}, {self.name}, "
                f"Created at: {self.created_at}, Last updated: {self.updated_at})")
