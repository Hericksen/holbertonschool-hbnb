from app.models.review import Review
from app.models.place import Place
from app.models.user import User
from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        # Dépôts en mémoire pour chaque entité
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()  # Repository pour les avis

    # --- Opérations sur les utilisateurs ---
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    # --- Opérations sur les lieux ---
    def create_place(self, place_data):
        # Validation des attributs
        price = place_data.get('price')
        latitude = place_data.get('latitude')
        longitude = place_data.get('longitude')
        if price < 0:
            raise ValueError("Le prix doit être positif ou nul.")
        if not (-90 <= latitude <= 90):
            raise ValueError("La latitude doit être comprise entre -90 et 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("La longitude doit être comprise entre -180 et 180.")

        # Vérifier que le propriétaire existe
        owner_id = place_data.get('owner_id')
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Propriétaire non trouvé.")

        # Créer le lieu
        place = Place(
            title=place_data.get('title'),
            description=place_data.get('description', ''),
            price=price,
            latitude=latitude,
            longitude=longitude,
            owner=owner,
            amenities=place_data.get('amenities', [])
        )
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        # Validation des nouveaux attributs
        if 'price' in place_data:
            if place_data['price'] < 0:
                raise ValueError("Le prix doit être positif ou nul.")
        if 'latitude' in place_data:
            if not (-90 <= place_data['latitude'] <= 90):
                raise ValueError("La latitude doit être comprise entre -90 et 90.")
        if 'longitude' in place_data:
            if not (-180 <= place_data['longitude'] <= 180):
                raise ValueError("La longitude doit être comprise entre -180 et 180.")
        # Si le propriétaire est mis à jour
        if 'owner_id' in place_data:
            owner = self.user_repo.get(place_data['owner_id'])
            if not owner:
                raise ValueError("Propriétaire non trouvé.")
            place_data['owner'] = owner
            del place_data['owner_id']
        place.update(place_data)
        return place

    # --- Opérations sur les avis ---
    def create_review(self, review_data):
        # Validation des attributs de l'avis
        user_id = review_data.get("user_id")
        place_id = review_data.get("place_id")
        rating = review_data.get("rating")

        # Vérification que l'utilisateur et le lieu existent
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé.")

        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Lieu non trouvé.")

        if rating < 1 or rating > 5:
            raise ValueError("La note doit être entre 1 et 5.")

        # Créer l'avis
        review = Review(
            text=review_data.get("text"),
            rating=rating,
            user=user,
            place=place
        )
        self.review_repo.add(review)

        # Ajouter l'avis au lieu correspondant
        place.reviews.append(review)

        # Retourner l'avis créé
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_reviews_by_place(self, place_id):
        # Obtenir les avis pour un lieu donné
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Lieu non trouvé.")
        return place.reviews

    def get_reviews_by_user(self, user_id):
        # Obtenir les avis laissés par un utilisateur donné
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé.")

        reviews = []
        for review in self.review_repo.get_all():
            if review.user.id == user.id:
                reviews.append(review)
        return reviews
