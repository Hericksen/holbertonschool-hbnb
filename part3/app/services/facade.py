from app.services.repositories.user_repository import UserRepository
from app.services.repositories.place_repository import PlaceRepository
from app.services.repositories.review_repository import ReviewRepository
from app.services.repositories.amenity_repository import AmenityRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    def _user_to_dict(self, user_obj):
        if not user_obj:
            return None
        return {
            "id": user_obj.id,
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "email": user_obj.email,
            "is_admin": getattr(user_obj, 'is_admin', False)
        }

    def _amenity_to_dict(self, amenity_obj):
        if not amenity_obj:
            return None
        return {
            "id": amenity_obj.id,
            "name": amenity_obj.name
        }

    def _place_to_dict(self, place_obj):
        if not place_obj:
            return None
        return {
            "id": place_obj.id,
            "title": place_obj.title,
            "description": place_obj.description,
            "price": place_obj.price,
            "latitude": place_obj.latitude,
            "longitude": place_obj.longitude,
            "owner_id": place_obj.owner.id,
            "amenities": [a.id for a in place_obj.amenities] if hasattr(place_obj, "amenities") else []
        }

    def _review_to_dict(self, review_obj):
        if not review_obj:
            return None
        return {
            "id": review_obj.id,
            "text": review_obj.text,
            "rating": review_obj.rating,
            "user_id": review_obj.user.id,
            "place_id": review_obj.place.id
        }

    # USERS
    def create_user(self, user_data):
        user = User(**user_data)
        user.hash_password(user_data['password'])
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_id(self, user_id):  # utilisé dans admin_required()
        return self.get_user(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        users = self.user_repo.get_all()
        return [self._user_to_dict(user) for user in users]

    def update_user(self, user_id, user_data):
        user = self.get_user(user_id)
        if user:
            if "password" in user_data:
                user.hash_password(user_data["password"])
                user_data.pop("password")
            for key, value in user_data.items():
                setattr(user, key, value)
            self.user_repo.update(user)
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            # Supprime d'abord les places et critiques associées
            for place in user.places:
                self.place_repo.delete(place)
            for review in user.reviews:
                self.review_repo.delete(review)

            # Puis supprime l'utilisateur
            self.user_repo.delete(user)
            return True
        return False

    # AMENITIES
    def create_amenity(self, amenity_data):
        name = amenity_data.get("name", "")
        if not name or len(name) > 50:
            raise ValueError("Invalid 'name': must be non-empty and ≤ 50 characters.")
        owner_id = amenity_data.get("owner_id")
        amenity_obj = Amenity(name=name, owner_id=owner_id)
        self.amenity_repo.add(amenity_obj)
        return amenity_obj

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        amenity.update(data)
        self.amenity_repo.add(amenity)
        return amenity

    def delete_amenity(self, amenity_id):
        amenity = self.amenity_repo.get(amenity_id)
        if amenity:
            self.amenity_repo.delete(amenity)
            return True
        return False

    # PLACES
    def create_place(self, place_data):
        if place_data["price"] < 0:
            raise ValueError("Price must be a non-negative value.")
        if not (-90 <= place_data["latitude"] <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if not (-180 <= place_data["longitude"] <= 180):
            raise ValueError("Longitude must be between -180 and 180.")

        owner = self.user_repo.get(place_data["owner_id"])
        if not owner:
            raise ValueError("Owner not found.")

        place_obj = Place(
            title=place_data["title"],
            description=place_data.get("description", ""),
            price=place_data["price"],
            latitude=place_data["latitude"],
            longitude=place_data["longitude"],
            owner=owner
        )
        place_obj.amenities = []

        if "amenities" in place_data:
            for amenity_id in place_data["amenities"]:
                amenity_obj = self.amenity_repo.get(amenity_id)
                if amenity_obj:
                    place_obj.amenities.append(amenity_obj)

        self.place_repo.add(place_obj)
        return place_obj

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        if "price" in data and data["price"] < 0:
            raise ValueError("Price must be a non-negative value.")
        if "latitude" in data and not (-90 <= data["latitude"] <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if "longitude" in data and not (-180 <= data["longitude"] <= 180):
            raise ValueError("Longitude must be between -180 and 180.")

        if "owner_id" in data:
            new_owner = self.user_repo.get(data["owner_id"])
            if not new_owner:
                raise ValueError("Owner not found.")
            place.owner = new_owner
            data.pop("owner_id")

        if "amenities" in data:
            new_amenities = []
            for amenity_id in data["amenities"]:
                amenity_obj = self.amenity_repo.get(amenity_id)
                if amenity_obj:
                    new_amenities.append(amenity_obj)
            place.amenities = new_amenities
            data.pop("amenities")

        place.update(data)
        self.place_repo.add(place)
        return place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place:
            self.place_repo.delete(place)
            return True
        return False

    # REVIEWS
    def create_review(self, review_data):
        required = ["text", "rating", "user_id", "place_id"]
        for field in required:
            if field not in review_data:
                raise ValueError(f"Missing required field: {field}")

        if not (1 <= review_data["rating"] <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        user = self.user_repo.get(review_data["user_id"])
        if not user:
            raise ValueError("User not found.")
        place = self.place_repo.get(review_data["place_id"])
        if not place:
            raise ValueError("Place not found.")

        review_obj = Review(
            text=review_data["text"],
            rating=review_data["rating"],
            user=user,
            place=place
        )
        self.review_repo.add(review_obj)
        return review_obj

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all() if r.place.id == place_id]

    def update_review(self, review_id, data):
        review = self.review_repo.get(review_id)
        if not review:
            return None
        if "rating" in data and not (1 <= data["rating"] <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        review.update(data)
        self.review_repo.add(review)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if review:
            self.review_repo.delete(review)
            return True
        return False


facade = HBnBFacade()
