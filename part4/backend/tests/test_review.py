import unittest
import uuid
from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review

class TestReviewModel(unittest.TestCase):
    """
    This test case verifies the behavior of the Review model, including
    creation and validation of text, rating, user, and place.
    """

    def setUp(self):
        """
        Set up a test application context and create all tables in an in-memory database.
        Also clear User.existing_emails to avoid collisions in user creation.
        """
        self.app = create_app("config.TestConfig")  # Adapt if your TestConfig is named differently
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear the existing_emails set to avoid collisions across tests
        User.existing_emails.clear()

        # Create a user for testing
        unique_email_user = f"{uuid.uuid4()}@example.com"
        self.user = User(
            first_name="Review",
            last_name="Tester",
            email=unique_email_user,
            password="reviewpass"
        )
        db.session.add(self.user)
        db.session.commit()

        # Create a place for testing
        unique_email_owner = f"{uuid.uuid4()}@example.com"
        self.owner = User(
            first_name="Owner",
            last_name="Place",
            email=unique_email_owner,
            password="ownerpass"
        )
        db.session.add(self.owner)
        db.session.commit()

        self.place = Place(
            title="Review Place",
            description="A place to review",
            price=50,
            latitude=45.0,
            longitude=10.0,
            owner=self.owner
        )
        db.session.add(self.place)
        db.session.commit()

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_valid_review(self):
        """
        Test creating a valid review with text, rating, user, and place.
        """
        review = Review(
            text="Great place!",
            rating=5,
            user=self.user,
            place=self.place
        )
        db.session.add(review)
        db.session.commit()

        retrieved = Review.query.get(review.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.text, "Great place!")
        self.assertEqual(retrieved.rating, 5)
        self.assertEqual(retrieved.user_id, self.user.id)
        self.assertEqual(retrieved.place_id, self.place.id)

    def test_create_review_empty_text(self):
        """
        Test creating a review with an empty text should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Review(
                text="",
                rating=4,
                user=self.user,
                place=self.place
            )

    def test_create_review_rating_out_of_range(self):
        """
        Test creating a review with a rating out of [1..5] should raise ValueError.
        """
        # Rating too low
        with self.assertRaises(ValueError):
            Review(
                text="Too low rating",
                rating=0,
                user=self.user,
                place=self.place
            )

        # Rating too high
        with self.assertRaises(ValueError):
            Review(
                text="Too high rating",
                rating=6,
                user=self.user,
                place=self.place
            )

    def test_create_review_invalid_user(self):
        """
        Test creating a review with an invalid user should raise TypeError.
        """
        with self.assertRaises(TypeError):
            Review(
                text="No user object",
                rating=3,
                user="not_a_user",
                place=self.place
            )

    def test_create_review_invalid_place(self):
        """
        Test creating a review with an invalid place should raise TypeError.
        """
        with self.assertRaises(TypeError):
            Review(
                text="No place object",
                rating=3,
                user=self.user,
                place="not_a_place"
            )


if __name__ == "__main__":
    unittest.main()
