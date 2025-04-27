from app.persistence.repositories.user_repository import UserRepository
from app.persistence.repositories.place_repository import PlaceRepository
from app.persistence.repositories.review_repository import ReviewRepository
from app.persistence.repositories.amenity_repository import AmenityRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_user_list(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        if not user_data:
            return 400
        user = self.get_user(user_id)
        if not user:
            return 404
        for key, value in user_data.items():
            setattr(user, key, value)
        return user

    def create_amenity(self, amenity_data):
       amenity = Amenity(**amenity_data)
       self.amenity_repo.add(amenity)
       return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return 404
        for key, value in amenity_data.items():
            setattr(amenity, key, value)
        return amenity

    def create_place(self, place_data):
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.get_place(place_id)
        if not place:
            return 404
        for key, value in place_data.items():
            setattr(place, key, value)
        return place

    def create_review(self, review_data):
        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        reviews = self.review_repo.get_all()
        place_reviews = []
        place = self.get_place(place_id)
        if not place:
            return "no place"
        for review in reviews:
            if review.place_id == place.id:
                place_reviews.append(review)
        if place_reviews == []:
            return "no review"
        return place_reviews

    def update_review(self, review_id, review_data):
        review = self.get_review(review_id)
        if not review:
            return 404
        for key, value in review_data.items():
            setattr(review, key, value)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            return 404
        return self.review_repo.delete(review_id)
