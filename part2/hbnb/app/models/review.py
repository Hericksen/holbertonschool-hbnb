# app/models/review.py

from app.models.base_model import BaseModel

class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place  # Instance de la classe Place
        self.user = user  # Instance de la classe User

    def __str__(self):
        return f"Review({self.id}, {self.rating}, {self.text})"
