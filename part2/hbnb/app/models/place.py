# app/models/place.py

from base_model import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner  # Instance de la classe User
        self.reviews = []  # Liste de reviews
        self.amenities = []  # Liste d'amenités

    def add_review(self, review):
        """Ajoute un avis au lieu"""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Ajoute une amenité au lieu"""
        self.amenities.append(amenity)

    def __str__(self):
        return f"Place({self.id}, {self.title}, {self.price})"
