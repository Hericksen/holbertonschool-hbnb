import unittest
from app import create_app, db
from app.services.facade import HBnBFacade
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class TestHBnBFacade(unittest.TestCase):
    """
    This test case verifies the functionality of the HBnBFacade class.
    It covers creating, retrieving, updating, and deleting users, amenities,
    places, and reviews.
    """

    def setUp(self):
        """
        Set up a test environment and create the database tables.
        """
        self.app = create_app("config.TestConfig")  # Make sure TestConfig is defined
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.facade = HBnBFacade()

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ------------------ USER TESTS ------------------

    def test_create_user_success(self):
        """
        Test creating a user with valid data.
        """
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "secret123",
            "is_admin": True
        }
        user = self.facade.create_user(user_data)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "john@example.com")
        self.assertTrue(user.is_admin)

    def test_get_user_not_found(self):
        """
        Test retrieving a user that does not exist should return None.
        """
        user = self.facade.get_user("non-existent-id")
        self.assertIsNone(user)

    def test_update_user_success(self):
        """
        Test updating an existing user with new data.
        """
        user_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password": "alicepass",
            "is_admin": False
        }
        user = self.facade.create_user(user_data)
        update_data = {
            "first_name": "AliceUpdated",
            "password": "newpass"
        }
        updated = self.facade.update_user(user.id, update_data)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.first_name, "AliceUpdated")
        # Make sure password is updated (hashed)
        self.assertTrue(updated.verify_password("newpass"))

    def test_delete_user_success(self):
        """
        Test deleting an existing user.
        """
        user_data = {
            "first_name": "Bob",
            "last_name": "Marley",
            "email": "bob@example.com",
            "password": "bobpass",
            "is_admin": False
        }
        user = self.facade.create_user(user_data)
        result = self.facade.delete_user(user.id)
        self.assertTrue(result)
        self.assertIsNone(self.facade.get_user(user.id))

    # ------------------ AMENITY TESTS ------------------

    def test_create_amenity_success(self):
        """
        Test creating an amenity with a valid name.
        """
        amenity_data = {"name": "Pool"}
        amenity = self.facade.create_amenity(amenity_data)
        self.assertIsNotNone(amenity.id)
        self.assertEqual(amenity.name, "Pool")

    def test_create_amenity_invalid_name(self):
        """
        Test creating an amenity with an invalid (empty) name should raise ValueError.
        """
        amenity_data = {"name": ""}
        with self.assertRaises(ValueError):
            self.facade.create_amenity(amenity_data)

    def test_update_amenity_success(self):
        """
        Test updating an existing amenity.
        """
        amenity_data = {"name": "Wifi"}
        amenity = self.facade.create_amenity(amenity_data)
        updated_data = {"name": "High-Speed Wifi"}
        updated_amenity = self.facade.update_amenity(amenity.id, updated_data)
        self.assertIsNotNone(updated_amenity)
        self.assertEqual(updated_amenity.name, "High-Speed Wifi")

    def test_delete_amenity_success(self):
        """
        Test deleting an existing amenity.
        """
        amenity_data = {"name": "Sauna"}
        amenity = self.facade.create_amenity(amenity_data)
        result = self.facade.delete_amenity(amenity.id)
        self.assertTrue(result)
        self.assertIsNone(self.facade.get_amenity(amenity.id))

    # ------------------ PLACE TESTS ------------------

    def test_create_place_success(self):
        """
        Test creating a place with valid data.
        """
        # First, create an owner user
        owner_data = {
            "first_name": "Owner",
            "last_name": "Test",
            "email": "owner@example.com",
            "password": "ownerpass",
            "is_admin": False
        }
        owner = self.facade.create_user(owner_data)

        place_data = {
            "title": "Cozy Cabin",
            "description": "A nice and cozy place",
            "price": 100,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": owner.id
        }
        place = self.facade.create_place(place_data)
        self.assertIsNotNone(place.id)
        self.assertEqual(place.title, "Cozy Cabin")
        self.assertEqual(place.owner.id, owner.id)

    def test_create_place_invalid_price(self):
        """
        Test creating a place with a negative price should raise ValueError.
        """
        # Create an owner user
        owner_data = {
            "first_name": "Bad",
            "last_name": "Price",
            "email": "badprice@example.com",
            "password": "pass",
            "is_admin": False
        }
        owner = self.facade.create_user(owner_data)

        place_data = {
            "title": "Cheap Place",
            "description": "Price is negative",
            "price": -10,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": owner.id
        }
        with self.assertRaises(ValueError):
            self.facade.create_place(place_data)

    def test_update_place_success(self):
        """
        Test updating an existing place.
        """
        # Create user and place
        user_data = {
            "first_name": "Place",
            "last_name": "Owner",
            "email": "placeowner@example.com",
            "password": "placepass"
        }
        owner = self.facade.create_user(user_data)
        place_data = {
            "title": "Old Title",
            "description": "Old Desc",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": owner.id
        }
        place = self.facade.create_place(place_data)
        # Update
        updated_data = {
            "title": "New Title",
            "price": 75
        }
        updated_place = self.facade.update_place(place.id, updated_data)
        self.assertIsNotNone(updated_place)
        self.assertEqual(updated_place.title, "New Title")
        self.assertEqual(updated_place.price, 75)

    def test_delete_place_success(self):
        """
        Test deleting an existing place.
        """
        # Create user and place
        user_data = {
            "first_name": "Delete",
            "last_name": "Me",
            "email": "delme@example.com",
            "password": "delpass"
        }
        owner = self.facade.create_user(user_data)
        place_data = {
            "title": "Will be deleted",
            "description": "desc",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": owner.id
        }
        place = self.facade.create_place(place_data)

        result = self.facade.delete_place(place.id)
        self.assertTrue(result)
        self.assertIsNone(self.facade.get_place(place.id))

    # ------------------ REVIEW TESTS ------------------

    def test_create_review_success(self):
        """
        Test creating a review with valid data.
        """
        # Create user and place
        user_data = {
            "first_name": "Reviewer",
            "last_name": "Test",
            "email": "reviewer@example.com",
            "password": "reviewpass"
        }
        reviewer = self.facade.create_user(user_data)

        place_data = {
            "title": "Review Place",
            "description": "desc",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": reviewer.id
        }
        place = self.facade.create_place(place_data)

        review_data = {
            "text": "Great place!",
            "rating": 5,
            "user_id": reviewer.id,
            "place_id": place.id
        }
        review = self.facade.create_review(review_data)
        self.assertIsNotNone(review.id)
        self.assertEqual(review.text, "Great place!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user.id, reviewer.id)
        self.assertEqual(review.place.id, place.id)

    def test_create_review_missing_field(self):
        """
        Test creating a review with a missing required field should raise ValueError.
        """
        review_data = {
            "text": "Incomplete review",
            "rating": 4,
            # missing user_id and place_id
        }
        with self.assertRaises(ValueError):
            self.facade.create_review(review_data)

    def test_update_review_success(self):
        """
        Test updating an existing review.
        """
        # Create user, place, and review
        user_data = {
            "first_name": "UpdateReview",
            "last_name": "User",
            "email": "update_review@example.com",
            "password": "pass"
        }
        user = self.facade.create_user(user_data)

        place_data = {
            "title": "Review Update Place",
            "description": "desc",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": user.id
        }
        place = self.facade.create_place(place_data)

        review_data = {
            "text": "Initial text",
            "rating": 3,
            "user_id": user.id,
            "place_id": place.id
        }
        review = self.facade.create_review(review_data)

        # Update
        updated_data = {"text": "Updated text", "rating": 4}
        updated_review = self.facade.update_review(review.id, updated_data)
        self.assertIsNotNone(updated_review)
        self.assertEqual(updated_review.text, "Updated text")
        self.assertEqual(updated_review.rating, 4)

    def test_delete_review_success(self):
        """
        Test deleting an existing review.
        """
        # Create user, place, and review
        user_data = {
            "first_name": "DeleteReview",
            "last_name": "User",
            "email": "deletereview@example.com",
            "password": "pass"
        }
        user = self.facade.create_user(user_data)

        place_data = {
            "title": "DeleteReview Place",
            "description": "desc",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": user.id
        }
        place = self.facade.create_place(place_data)

        review_data = {
            "text": "To be deleted",
            "rating": 2,
            "user_id": user.id,
            "place_id": place.id
        }
        review = self.facade.create_review(review_data)

        result = self.facade.delete_review(review.id)
        self.assertTrue(result)
        self.assertIsNone(self.facade.get_review(review.id))

if __name__ == "__main__":
    unittest.main()
