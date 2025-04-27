import unittest
import uuid
import re
from app import create_app, db
from app.models.user import User

class TestUserModel(unittest.TestCase):
    """
    This test case verifies the behavior of the User model, including
    validations for names, email, password hashing, and the unique email constraint.
    """

    def setUp(self):
        """
        Set up a test application context and create all tables
        in an in-memory database. Also clear User.existing_emails to avoid collisions.
        """
        self.app = create_app("config.TestConfig")  # Adapt if your TestConfig is named differently
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear existing emails to avoid collisions between tests
        User.existing_emails.clear()

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_valid_user(self):
        """
        Test creating a valid user with all required fields.
        """
        email = f"{uuid.uuid4()}@example.com"
        user = User(
            first_name="Alice",
            last_name="Smith",
            email=email,
            password="secretpass"
        )
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.get(user.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.first_name, "Alice")
        self.assertEqual(retrieved.last_name, "Smith")
        self.assertEqual(retrieved.email, email)
        self.assertFalse(retrieved.is_admin)

    def test_create_user_first_name_too_long(self):
        """
        Test creating a user with a first_name over 50 characters should raise ValueError.
        """
        long_name = "A" * 51
        email = f"{uuid.uuid4()}@example.com"
        with self.assertRaises(ValueError):
            User(
                first_name=long_name,
                last_name="Smith",
                email=email,
                password="pass"
            )

    def test_create_user_last_name_too_long(self):
        """
        Test creating a user with a last_name over 50 characters should raise ValueError.
        """
        long_name = "B" * 51
        email = f"{uuid.uuid4()}@example.com"
        with self.assertRaises(ValueError):
            User(
                first_name="Bob",
                last_name=long_name,
                email=email,
                password="pass"
            )

    def test_create_user_invalid_email(self):
        """
        Test creating a user with an invalid email format should raise ValueError.
        """
        with self.assertRaises(ValueError):
            User(
                first_name="Invalid",
                last_name="Email",
                email="not_an_email",
                password="pass"
            )

    def test_create_user_duplicate_email(self):
        """
        Test creating two users with the same email should raise ValueError on the second one.
        """
        email = "duplicate@example.com"
        user1 = User(
            first_name="User1",
            last_name="Dup",
            email=email,
            password="pass1"
        )
        db.session.add(user1)
        db.session.commit()

        # Attempt to create user2 with the same email
        with self.assertRaises(ValueError):
            User(
                first_name="User2",
                last_name="Dup",
                email=email,
                password="pass2"
            )

    def test_password_hashing_and_verification(self):
        """
        Test that the password is hashed and verify_password works correctly.
        """
        email = f"{uuid.uuid4()}@example.com"
        user = User(
            first_name="Hash",
            last_name="Test",
            email=email,
            password="mypassword"
        )
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.get(user.id)
        self.assertTrue(retrieved.verify_password("mypassword"))
        self.assertFalse(retrieved.verify_password("wrongpassword"))

    def test_is_admin_flag(self):
        """
        Test that the is_admin flag defaults to False unless specified.
        """
        email1 = f"{uuid.uuid4()}@example.com"
        user1 = User(
            first_name="Admin",
            last_name="False",
            email=email1,
            password="pass"
        )
        self.assertFalse(user1.is_admin)

        email2 = f"{uuid.uuid4()}@example.com"
        user2 = User(
            first_name="Admin",
            last_name="True",
            email=email2,
            password="pass",
            is_admin=True
        )
        self.assertTrue(user2.is_admin)

    def test_to_dict_excludes_password(self):
        """
        Test that to_dict() returns a dictionary without the password field.
        """
        email = f"{uuid.uuid4()}@example.com"
        user = User(
            first_name="Dict",
            last_name="Test",
            email=email,
            password="secret"
        )
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()
        self.assertNotIn("password", user_dict)
        self.assertEqual(user_dict["email"], email)

if __name__ == "__main__":
    unittest.main()
