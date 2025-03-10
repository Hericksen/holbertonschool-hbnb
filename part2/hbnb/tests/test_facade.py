import unittest
from app.services.facade import HBnBFacade
from app.models.user import User


class TestHBnBFacade(unittest.TestCase):
    def setUp(self):
        """
        Resets the state before each test:
          - We empty the list of existing emails to avoid "This email is already in use."
          - We instantiate the facade
          - We create a default user (object) to be able to create places/reviews
        """
        User.existing_emails.clear()  # if your User class manages the uniqueness of emails
        self.facade = HBnBFacade()

        # Creating a default user
        self.user = self.facade.create_user({
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "alice@example.com"
        })

    # =========================
    # 1) TESTS FOR USERS
    # =========================
    def test_create_user(self):
        """Testing to create a valid user (object)"""
        new_user = self.facade.create_user({
            "first_name": "Bob",
            "last_name": "Marley",
            "email": "bob@example.com"
        })
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.first_name, "Bob")
        self.assertEqual(new_user.last_name, "Marley")

    def test_create_user_duplicate_email(self):
        """Test creating a user with an email already in use"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_user({
                "first_name": "Alice2",
                "last_name": "Doe2",
                "email": "alice@example.com"
            })
        self.assertIn("This email is already in use", str(ctx.exception))

    def test_create_user_invalid_first_name(self):
        """Test user with empty first_name (if your User class checks for this)"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_user({
                "first_name": "",
                "last_name": "Test",
                "email": "test@example.com"
            })
        self.assertIn("first_name invalide", str(ctx.exception))

    def test_create_user_invalid_last_name(self):
        """Test user with empty last_name"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_user({
                "first_name": "Charlie",
                "last_name": "",
                "email": "charlie@example.com"
            })
        self.assertIn("last_name invalide", str(ctx.exception))

    def test_create_user_invalid_email_format(self):
        """User test with incorrectly formatted email"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_user({
                "first_name": "Diana",
                "last_name": "Doe",
                "email": "not-an-email"
            })
        self.assertIn("Invalid email format", str(ctx.exception))

    # =========================
    # 2) TESTS FOR AMENITIES
    # =========================
    def test_create_amenity_valid(self):
        """Test to create a valid Amenity"""
        amenity = self.facade.create_amenity({"name": "Piscine"})
        self.assertIsNotNone(amenity.id)
        self.assertEqual(amenity.name, "Piscine")

    def test_create_amenity_invalid_empty_name(self):
        """Amenity test with empty name"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_amenity({"name": ""})
        self.assertIn("non-empty", str(ctx.exception))

    def test_update_amenity(self):
        """Updated test of an Amenity"""
        amenity = self.facade.create_amenity({"name": "Garden"})
        updated = self.facade.update_amenity(
            amenity.id, {"name": "Big Garden"})
        self.assertEqual(updated.name, "Big Garden")

    def test_get_all_amenities(self):
        """Test recovery of all Amenities"""
        self.facade.create_amenity({"name": "WiFi"})
        self.facade.create_amenity({"name": "TV"})
        amenities = self.facade.get_all_amenities()
        self.assertTrue(len(amenities) >= 2)

    # =========================
    # 3) TESTS FOR PLACES
    # =========================
    def test_create_place_valid(self):
        """Test to create a valid Place"""
        place_data = {
            "title": "Central Apartment",
            "description": "Nice place in city center",
            "price": 150.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        }
        place = self.facade.create_place(place_data)
        self.assertEqual(place.title, "Central Apartment")
        self.assertEqual(place.price, 150.0)
        self.assertEqual(place.latitude, 48.8566)
        self.assertEqual(place.longitude, 2.3522)
        self.assertEqual(place.owner.id, self.user.id)

    def test_create_place_invalid_price(self):
        """Test Place with negative price"""
        place_data = {
            "title": "Cheap Apartment",
            "description": "Price is negative",
            "price": -10.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("non-negative", str(ctx.exception))

    def test_create_place_invalid_latitude_high(self):
        """Test Place with latitude > 90"""
        place_data = {
            "title": "Out of Bounds Latitude",
            "description": "Lat = 91.0",
            "price": 50.0,
            "latitude": 91.0,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("Latitude must be between -90 and 90",
                      str(ctx.exception))

    def test_create_place_invalid_latitude_low(self):
        """Test Place with latitude < -90"""
        place_data = {
            "title": "Out of Bounds Latitude",
            "description": "Lat = -91.0",
            "price": 50.0,
            "latitude": -91.0,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("Latitude must be between -90 and 90",
                      str(ctx.exception))

    def test_create_place_invalid_longitude_high(self):
        """Test Place with longitude > 180"""
        place_data = {
            "title": "Out of Bounds Longitude",
            "description": "Long = 181.0",
            "price": 50.0,
            "latitude": 48.8566,
            "longitude": 181.0,
            "owner_id": self.user.id,
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("Longitude must be between -180 and 180",
                      str(ctx.exception))

    def test_create_place_invalid_longitude_low(self):
        """Test Place with longitude < -180"""
        place_data = {
            "title": "Out of Bounds Longitude",
            "description": "Long = -181.0",
            "price": 50.0,
            "latitude": 48.8566,
            "longitude": -181.0,
            "owner_id": self.user.id,
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("Longitude must be between -180 and 180",
                      str(ctx.exception))

    def test_create_place_no_owner(self):
        """Test Place with nonexistent owner_id"""
        place_data = {
            "title": "No Owner",
            "description": "Owner not found",
            "price": 50.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": "non-existent-id",
            "amenities": []
        }
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_place(place_data)
        self.assertIn("Owner not found", str(ctx.exception))

    def test_get_place_not_found(self):
        """Test get_place with nonexistent id"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.get_place("non-existent-id")
        self.assertIn("Place not found", str(ctx.exception))

    def test_get_all_places(self):
        """Test recovery of all Places"""
        self.facade.create_place({
            "title": "Apartment 1",
            "description": "First apt",
            "price": 100.0,
            "latitude": 40.0,
            "longitude": 3.0,
            "owner_id": self.user.id,
            "amenities": []
        })
        self.facade.create_place({
            "title": "Apartment 2",
            "description": "Second apt",
            "price": 200.0,
            "latitude": 41.0,
            "longitude": 4.0,
            "owner_id": self.user.id,
            "amenities": []
        })
        places = self.facade.get_all_places()
        self.assertTrue(len(places) >= 2)

    def test_update_place_change_owner_and_amenities(self):
        # Create a second user to test the change of owner
        second_user = self.facade.create_user({
            "first_name": "Bob",
            "last_name": "Marley",
            "email": "bob@example.com"
        })

        # Create some amenities
        wifi = self.facade.create_amenity({"name": "WiFi"})
        pool = self.facade.create_amenity({"name": "Pool"})

        # Create a place with self.user as owner
        place_data = {
            "title": "Initial Title",
            "description": "Initial desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        }
        place = self.facade.create_place(place_data)

        # Build the new data
        update_data = {
            "title": "Updated Title",
            "price": 120.0,
            "owner_id": second_user.id,
            "amenities": [wifi.id, pool.id]
        }

        updated_place = self.facade.update_place(place.id, update_data)
        self.assertIsNotNone(updated_place)
        self.assertEqual(updated_place.title, "Updated Title")
        self.assertEqual(updated_place.price, 120.0)
        self.assertEqual(updated_place.owner.id, second_user.id)
        self.assertIn(wifi, updated_place.amenities)
        self.assertIn(pool, updated_place.amenities)

    # =========================
    # 4) TESTS FOR REVIEWS
    # =========================
    def test_create_review_valid(self):
        """Test creation of a valid Review"""
        place = self.facade.create_place({
            "title": "Review Place",
            "description": "desc",
            "price": 150.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        review = self.facade.create_review({
            "text": "Great place!",
            "rating": 5,
            "user_id": self.user.id,
            "place_id": place.id
        })
        self.assertIsNotNone(review.id)
        self.assertEqual(review.text, "Great place!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user.id, self.user.id)
        self.assertEqual(review.place.id, place.id)

    def test_create_review_invalid_rating(self):
        """Test Review with rating excluding [1..5]"""
        place = self.facade.create_place({
            "title": "Rating Place",
            "description": "desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_review({
                "text": "Bad rating",
                "rating": 6,
                "user_id": self.user.id,
                "place_id": place.id
            })
        self.assertIn("between 1 and 5", str(ctx.exception))

    def test_create_review_missing_text(self):
        """Test Review without 'text' field"""
        place = self.facade.create_place({
            "title": "Missing text place",
            "description": "desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_review({
                # "text": "Should be here",
                "rating": 4,
                "user_id": self.user.id,
                "place_id": place.id
            })
        self.assertIn("Missing required field: text", str(ctx.exception))

    def test_create_review_missing_rating(self):
        """Test Review without 'rating' field"""
        place = self.facade.create_place({
            "title": "Missing rating place",
            "description": "desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_review({
                "text": "No rating provided",
                # "rating": 4,
                "user_id": self.user.id,
                "place_id": place.id
            })
        self.assertIn("Missing required field: rating", str(ctx.exception))

    def test_create_review_no_user(self):
        """Test Review with nonexistent user_id"""
        place = self.facade.create_place({
            "title": "No user place",
            "description": "desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_review({
                "text": "User not found test",
                "rating": 4,
                "user_id": "non-existent-id",
                "place_id": place.id
            })
        self.assertIn("User not found", str(ctx.exception))

    def test_create_review_no_place(self):
        """Test Review with non-existent place_id"""
        with self.assertRaises(ValueError) as ctx:
            self.facade.create_review({
                "text": "Place not found test",
                "rating": 4,
                "user_id": self.user.id,
                "place_id": "non-existent-id"
            })
        self.assertIn("Place not found", str(ctx.exception))

    def test_get_reviews_by_place(self):
        """Test retrieval of reviews for a given place"""
        place1 = self.facade.create_place({
            "title": "Place 1",
            "description": "desc",
            "price": 100.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        place2 = self.facade.create_place({
            "title": "Place 2",
            "description": "desc",
            "price": 200.0,
            "latitude": 49.0,
            "longitude": 3.0,
            "owner_id": self.user.id,
            "amenities": []
        })
        self.facade.create_review({
            "text": "Review for place1 - 1",
            "rating": 5,
            "user_id": self.user.id,
            "place_id": place1.id
        })
        self.facade.create_review({
            "text": "Review for place1 - 2",
            "rating": 4,
            "user_id": self.user.id,
            "place_id": place1.id
        })
        self.facade.create_review({
            "text": "Review for place2",
            "rating": 3,
            "user_id": self.user.id,
            "place_id": place2.id
        })
        reviews_place1 = self.facade.get_reviews_by_place(place1.id)
        reviews_place2 = self.facade.get_reviews_by_place(place2.id)
        self.assertEqual(len(reviews_place1), 2)
        self.assertEqual(len(reviews_place2), 1)

    def test_update_review(self):
        """Test update of a Review"""
        place = self.facade.create_place({
            "title": "Review Update Place",
            "description": "desc",
            "price": 150.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        review = self.facade.create_review({
            "text": "Initial review",
            "rating": 3,
            "user_id": self.user.id,
            "place_id": place.id
        })
        updated = self.facade.update_review(review.id, {
            "text": "Updated review",
            "rating": 4
        })
        self.assertEqual(updated.text, "Updated review")
        self.assertEqual(updated.rating, 4)

    def test_delete_review(self):
        """Test deletion of a Review"""
        place = self.facade.create_place({
            "title": "Review Delete Place",
            "description": "desc",
            "price": 150.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user.id,
            "amenities": []
        })
        review = self.facade.create_review({
            "text": "Review to delete",
            "rating": 3,
            "user_id": self.user.id,
            "place_id": place.id
        })
        deleted = self.facade.delete_review(review.id)
        self.assertEqual(deleted.id, review.id)
        # After removal, get_review should return None
        self.assertIsNone(self.facade.get_review(review.id))


if __name__ == "__main__":
    unittest.main()