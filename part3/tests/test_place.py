import unittest
import uuid
from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

class TestPlaceModel(unittest.TestCase):
    """
    This test case verifies the behavior of the Place model, including
    creation, validations, and adding reviews/amenities.
    """

    def setUp(self):
        """
        Set up a test application context and create all tables
        in an in-memory database. Also clear User.existing_emails to avoid
        'This email is already in use' errors across multiple tests.
        """
        self.app = create_app("config.TestConfig")  # Adapt if your TestConfig is named differently
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear the existing_emails set to avoid collisions between tests
        User.existing_emails.clear()

        # Create a user to be the owner of places (with a unique email)
        unique_email = f"{uuid.uuid4()}@example.com"
        self.user = User(
            first_name="John",
            last_name="Doe",
            email=unique_email,
            password="password"
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_valid_place(self):
        """
        Test creating a valid place with correct attributes.
        """
        place = Place(
            title="Cozy Cottage",
            description="A nice place to stay",
            price=100,
            latitude=45.0,
            longitude=10.0,
            owner=self.user
        )
        db.session.add(place)
        db.session.commit()

        retrieved = Place.query.get(place.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Cozy Cottage")
        self.assertEqual(retrieved.owner_id, self.user.id)

    def test_create_place_invalid_title(self):
        """
        Test creating a place with an empty or too long title should raise ValueError.
        """
        # Empty title
        with self.assertRaises(ValueError):
            Place(
                title="",
                description="desc",
                price=50,
                latitude=45.0,
                longitude=10.0,
                owner=self.user
            )

        # Title too long
        long_title = "a" * 101
        with self.assertRaises(ValueError):
            Place(
                title=long_title,
                description="desc",
                price=50,
                latitude=45.0,
                longitude=10.0,
                owner=self.user
            )

    def test_create_place_negative_price(self):
        """
        Test creating a place with a negative price should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Place(
                title="Negative Price Place",
                description="desc",
                price=-10,
                latitude=45.0,
                longitude=10.0,
                owner=self.user
            )

    def test_create_place_invalid_latitude(self):
        """
        Test creating a place with an out-of-range latitude should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Place(
                title="Invalid Latitude",
                description="desc",
                price=50,
                latitude=100.0,  # Out of [-90, 90]
                longitude=10.0,
                owner=self.user
            )

    def test_create_place_invalid_longitude(self):
        """
        Test creating a place with an out-of-range longitude should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Place(
                title="Invalid Longitude",
                description="desc",
                price=50,
                latitude=45.0,
                longitude=200.0,  # Out of [-180, 180]
                owner=self.user
            )

    def test_create_place_invalid_owner(self):
        """
        Test creating a place with an invalid owner type should raise TypeError.
        """
        with self.assertRaises(TypeError):
            Place(
                title="TypeError Place",
                description="desc",
                price=50,
                latitude=45.0,
                longitude=10.0,
                owner="not_a_user"
            )

    def test_add_review_to_place(self):
        """
        Test adding a valid Review to a Place.
        """
        place = Place(
            title="Review Test Place",
            description="desc",
            price=50,
            latitude=45.0,
            longitude=10.0,
            owner=self.user
        )
        db.session.add(place)
        db.session.commit()

        review = Review(text="Great place!", rating=5, user=self.user, place=place)
        place.add_review(review)
        db.session.commit()

        self.assertIn(review, place.reviews)
        self.assertEqual(review.place.id, place.id)

    def test_add_amenity_to_place(self):
        """
        Test adding a valid Amenity to a Place.
        """
        place = Place(
            title="Amenity Test Place",
            description="desc",
            price=50,
            latitude=45.0,
            longitude=10.0,
            owner=self.user
        )
        db.session.add(place)
        db.session.commit()

        amenity = Amenity(name="Pool", owner_id=None)
        db.session.add(amenity)
        db.session.commit()

        place.add_amenity(amenity)
        db.session.commit()

        self.assertIn(amenity, place.amenities)
        self.assertIn(place, amenity.places)  # Because it's a many-to-many relationship

    def test_add_review_type_error(self):
        """
        Test adding an invalid object (not a Review) to a Place should raise TypeError.
        """
        place = Place(
            title="Bad Review Place",
            description="desc",
            price=50,
            latitude=45.0,
            longitude=10.0,
            owner=self.user
        )
        db.session.add(place)
        db.session.commit()

        with self.assertRaises(TypeError):
            place.add_review("not_a_review")

    def test_add_amenity_type_error(self):
        """
        Test adding an invalid object (not an Amenity) to a Place should raise TypeError.
        """
        place = Place(
            title="Bad Amenity Place",
            description="desc",
            price=50,
            latitude=45.0,
            longitude=10.0,
            owner=self.user
        )
        db.session.add(place)
        db.session.commit()

        with self.assertRaises(TypeError):
            place.add_amenity("not_an_amenity")


if __name__ == "__main__":
    unittest.main()
