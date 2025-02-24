from part2.hbnb.app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Représente un service proposé (ex : Wi-Fi, Parking)."""

    def __init__(self, name):
        super().__init__()
        self.name = self.validate_name(name)

    def validate_name(self, name):
        if len(name) > 50:
            raise ValueError(
                "Le nom de l’amenity ne peut pas dépasser 50 caractères.")
        return name
