#!/user/bin/python3

from app.models.basemodel import BaseModel
from app import db

class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)

    def __init__(self, text, rating, place_id, user_id):
        super().__init__()
        self.text = self.validate_text(text)
        self.rating = self.validate_rating(rating)
        self.place_id = self.validate_place(place_id)
        self.user_id = self.validate_user(user_id)

    def validate_text(self, text):
        if not text:
            raise ValueError("Review text must be provided.")
        return text

    def validate_rating(self, rating):
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        return rating

    def validate_place(self, place_id):
        from app.services import facade
        place = facade.place_repo.get(place_id)
        if not place:
            raise ValueError("Place must be a valid Place instance.")
        return place_id

    def validate_user(self, user_id):
        from app.services import facade
        user = facade.user_repo.get(user_id)
        if not user:
            raise ValueError("User must be a valid User instance.")
        return user_id

    def __str__(self):
        return (f"Review({self.id}, {self.text[:30]}..., Rating: {self.rating}, "
                f"Place: {self.place.title}, User: {self.user.first_name} {self.user.last_name}, "
                f"Created at: {self.created_at}, Last updated: {self.updated_at})")
