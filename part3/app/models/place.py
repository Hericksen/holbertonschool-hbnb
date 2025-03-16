from app import db
from app.models.BaseModel import BaseModel

# Association table for many-to-many relationship between Place and Amenity
place_amenity = db.Table('place_amenity',
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
)


class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Clé étrangère vers la table users
    owner_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    # Relation directe : permet de faire place.owner pour accéder à l'objet User
    owner = db.relationship('User', backref='places', lazy=True)

    # Relation vers Review et Amenity
    reviews = db.relationship('Review', backref='place', lazy=True)
    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        lazy='subquery',
        backref=db.backref('places', lazy=True)
    )

    """
    Place class.
    Attributes:
      - id (from BaseModel)
      - title: Required, max 100 characters
      - description: Optional
      - price: Float, must be >= 0
      - latitude: must be in [-90, 90]
      - longitude: must be in [-180, 180]
      - owner_id: foreign key to the users table
      - owner: User object (relationship)
      - reviews: List of associated reviews
      - amenities: List of associated amenities
    """

    def __init__(self, title, description, price, latitude, longitude, owner):
        """
        Initialise un objet Place.
        Le paramètre 'owner' doit être une instance de User.
        """
        super().__init__()

        # Validation du titre
        if not title or len(title) > 100:
            raise ValueError(
                "Invalid 'title': must be non-empty and ≤ 100 characters."
            )

        # Validation du prix
        if price < 0:
            raise ValueError("Invalid 'price': must be a positive number.")

        # Validation de la latitude
        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid 'latitude': must be between -90 and 90.")

        # Validation de la longitude
        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid 'longitude': must be between -180 and 180.")

        # Validation du propriétaire (owner)
        from .user import User  # Import local pour éviter les import circulaires
        if not isinstance(owner, User):
            raise TypeError("Expected 'owner' to be an instance of User.")

        # Affectation des champs
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner.id  # l'ID de l'utilisateur
        # SQLAlchemy gérera automatiquement self.owner grâce à la relation

    def add_review(self, review):
        """Adds a Review to the Place."""
        from .review import Review
        if not isinstance(review, Review):
            raise TypeError("Expected 'review' to be an instance of Review.")
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Adds an Amenity to the Place."""
        from .amenity import Amenity
        if not isinstance(amenity, Amenity):
            raise TypeError("Expected 'amenity' to be an instance of Amenity.")
        if amenity not in self.amenities:
            self.amenities.append(amenity)
