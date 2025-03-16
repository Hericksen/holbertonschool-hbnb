from app import db
from app.models.BaseModel import BaseModel


class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey(
        'places.id'), nullable=False)
    """
    Review class.
    Attributes:
      - id (from BaseModel)
      - text: Required (content of the review)
      - rating: Integer, must be between 1 and 5
      - place: Place being reviewed
      - user: User who wrote the review
      - created_at (from BaseModel)
      - updated_at (from BaseModel)

    Validation:
      - text must not be empty
      - rating must be between 1 and 5
    """

    def __init__(self, text, rating, user, place):
        super().__init__()

        if not text:
            raise ValueError("Invalid 'text': must be non-empty.")
        if not (1 <= rating <= 5):
            raise ValueError("Invalid 'rating': must be between 1 and 5.")

        from .user import User
        from .place import Place
        if not isinstance(user, User):
            raise TypeError("Expected 'user' to be an instance of User.")
        if not isinstance(place, Place):
            raise TypeError("Expected 'place' to be an instance of Place.")

        self.text = text
        self.rating = rating
        self.user_id = user.id
        self.place_id = place.id
