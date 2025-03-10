import unittest
from unittest import mock
from app.models.user import User
from app.models.place import Place
from app.models.review import Review


class TestUser(unittest.TestCase):

    def setUp(self):
        """Resets existing emails before each test."""
        User.existing_emails.clear()

    def test_valid_user_creation(self):
        """Tests the creation of a valid user."""
        user = User("Alice", "Dupont", "alice.dupont@example.com")
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Dupont")
        self.assertEqual(user.email, "alice.dupont@example.com")
        self.assertFalse(user.is_admin)

    def test_invalid_first_name_empty(self):
        """Tests if an empty first name triggers an error."""
        with self.assertRaises(ValueError):
            User("", "Dupont", "alice.dupont@example.com")

    def test_invalid_first_name_too_long(self):
        """Test if a first name that is too long triggers an error."""
        with self.assertRaises(ValueError):
            User("A" * 51, "Dupont", "alice.dupont@example.com")

    def test_invalid_last_name_empty(self):
        """Tests if an empty last name triggers an error."""
        with self.assertRaises(ValueError):
            User("Alice", "", "alice.dupont@example.com")

    def test_invalid_last_name_too_long(self):
        """Tests if a last name that is too long triggers an error."""
        with self.assertRaises(ValueError):
            User("Alice", "D" * 51, "alice.dupont@example.com")

    def test_invalid_email_format(self):
        """Tests if a malformed email triggers an error."""
        with self.assertRaises(ValueError):
            User("Alice", "Dupont", "alice.dupont.com")

    def test_duplicate_email(self):
        """Tests if email duplication is prohibited."""
        User("Alice", "Dupont", "alice.dupont@example.com")
        with self.assertRaises(ValueError):
            User("Bob", "Martin", "alice.dupont@example.com")

    def test_add_place(self):
        """Test if a location can be added to the user."""
        user = User("Alice", "Dupont", "alice.dupont@example.com")
        place_mock = mock.Mock(spec=Place)  # Specify the mock for Place
        user.add_place(place_mock)
        self.assertIn(place_mock, user.places)

    def test_add_review(self):
        """Tests if a notice can be added to the user."""
        user = User("Alice", "Dupont", "alice.dupont@example.com")
        review_mock = mock.Mock(spec=Review)  # Specify the mock for Review
        user.add_review(review_mock)
        self.assertIn(review_mock, user.reviews)


if __name__ == '__main__':
    unittest.main()
# Run the test with: python3 -m unittest tests/test_user.py
    # ou python3 -m pytest tests/test_user.py