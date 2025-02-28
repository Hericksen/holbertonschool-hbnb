from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.amenities = []
        self.next_amenity_id = 1

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
        price = place_data.get('price')
        latitude = place_data.get('latitude')
        longitude = place_data.get('longitude')
        if price < 0:
            raise ValueError("Le prix doit être positif ou nul.")
        if not (-90 <= latitude <= 90):
            raise ValueError("La latitude doit être comprise entre -90 et 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("La longitude doit être comprise entre -180 et 180.")

        owner_id = place_data.get('owner_id')
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Propriétaire non trouvé.")

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
        if 'price' in place_data and place_data['price'] < 0:
            raise ValueError("Le prix doit être positif ou nul.")
        if 'latitude' in place_data and not (-90 <= place_data['latitude'] <= 90):
            raise ValueError("La latitude doit être comprise entre -90 et 90.")
        if 'longitude' in place_data and not (-180 <= place_data['longitude'] <= 180):
            raise ValueError("La longitude doit être comprise entre -180 et 180.")
        if 'owner_id' in place_data:
            owner = self.user_repo.get(place_data['owner_id'])
            if not owner:
                raise ValueError("Propriétaire non trouvé.")
            place_data['owner'] = owner
            del place_data['owner_id']
        place.update(place_data)
        return place

    # --- Opérations sur les commodités ---
    def create_amenity(self, amenity_data):
        amenity = {"id": self.next_amenity_id, **amenity_data}
        self.amenities.append(amenity)
        self.next_amenity_id += 1
        return amenity

    def get_amenity(self, amenity_id):
        return next((a for a in self.amenities if a["id"] == amenity_id), None)

    def get_all_amenities(self):
        return self.amenities

    def update_amenity(self, amenity_id, amenity_data):
        for amenity in self.amenities:
            if amenity["id"] == amenity_id:
                amenity.update(amenity_data)
                return amenity
        return None

    def delete_amenity(self, amenity_id):
        for amenity in self.amenities:
            if amenity["id"] == amenity_id:
                self.amenities.remove(amenity)
                return True
        return False
