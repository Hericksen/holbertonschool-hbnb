from part2.hbnb.app.models.base_model import BaseModel


class Place(BaseModel):
    """Représente un logement disponible à la location."""

    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
        self.title = self.validate_title(title)
        self.description = description
        self.price = self.validate_price(price)
        self.latitude = self.validate_latitude(latitude)
        self.longitude = self.validate_longitude(longitude)
        self.owner = owner  # Instance de User
        self.reviews = []
        self.amenities = []

    def validate_title(self, title):
        if len(title) > 100:
            raise ValueError("Le titre ne peut pas dépasser 100 caractères.")
        return title

    def validate_price(self, price):
        if price <= 0:
            raise ValueError("Le prix doit être un nombre positif.")
        return price

    def validate_latitude(self, lat):
        if not (-90.0 <= lat <= 90.0):
            raise ValueError("Latitude invalide (-90 à 90).")
        return lat

    def validate_longitude(self, lon):
        if not (-180.0 <= lon <= 180.0):
            raise ValueError("Longitude invalide (-180 à 180).")
        return lon
