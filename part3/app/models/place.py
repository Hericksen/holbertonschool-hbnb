#!/usr/bin/python3
'''creat class place'''

from app.models.basemodel import BaseModel
from app.models.review import Review
from app.models.amenity import Amenity
from app import db

place_amenity = db.Table('place_amenity',
                         db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
                         db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True))

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    owner_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', backref='places', lazy=True)

    reviews = db.relationship('Review', backref='place', lazy=True)
    amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery', backref=db.backref('places', lazy=True))

    def __init__(self, title, description, price, latitude, longitude, owner_id, amenities=None):
        super().__init__()
        self.title = self.validate_title(title)
        self.price = self.validate_price(price)
        self.latitude = self.validate_latitude(latitude)
        self.longitude = self.validate_longitude(longitude)
        self.owner_id = self.validate_owner(owner_id)

    def validate_title(self, title):
        if not title or len(title) > 100:
            raise ValueError("Title must be non-empty and less than or equal to 100 characters.")
        return title

    def validate_price(self, price):
        if price <= 0:
            raise ValueError("Price must be a positive value.")
        return price

    def validate_latitude(self, latitude):
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0.")
        return latitude

    def validate_longitude(self, longitude):
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0.")
        return longitude

    def validate_owner(self, owner_id):
        from app.services import facade
        owner = facade.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Owner must be a valid User instance.")
        return owner_id

    def add_review(self, review):
        if not isinstance(review, Review):
            raise TypeError("the review does not exist")
        self.reviews.append(review)

    def add_amenity(self, amenities):
        if not isinstance(amenities, Amenity):
            raise TypeError("the amenity does not exist")
        self.amenities.append(amenities)

    def list_reviews(self):
        for x in self.reviews:
            print(f"{x}")

    def list_amenities(self):
        for x in self.amenities:
            print(f"{x}")

    def __str__(self):
        return (f"Place({self.id}, {self.title}, {self.price}, "
                f"Latitude: {self.latitude}, Longitude: {self.longitude}, "
                f"Owner: {self.owner.first_name} {self.owner.last_name}, "
                f"Created at: {self.created_at}, Last updated: {self.updated_at})")
