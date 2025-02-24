from part2.hbnb.app.models.base_model import BaseModel


class Review(BaseModel):
    """Représente un avis sur un logement."""

    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = self.validate_text(text)
        self.rating = self.validate_rating(rating)
        self.place = place
        self.user = user

    def validate_text(self, text):
        if not text:
            raise ValueError("Le texte de l'avis est obligatoire.")
        return text

    def validate_rating(self, rating):
        if rating < 1 or rating > 5:
            raise ValueError("La note doit être entre 1 et 5.")
        return rating
