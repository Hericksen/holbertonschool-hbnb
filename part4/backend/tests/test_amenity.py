import unittest
from app import create_app, db
from app.models.amenity import Amenity

class AmenityModelTestCase(unittest.TestCase):
    """
    This test case verifies the behavior of the Amenity model.
    """

    def setUp(self):
        """
        Prepare a test context and an in-memory database (or any test configuration).
        """
        self.app = create_app("config.TestConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_valid_amenity(self):
        """
        Test creating a valid amenity with a non-empty name.
        """
        amenity = Amenity(name="Pool")
        db.session.add(amenity)
        db.session.commit()

        retrieved = Amenity.query.get(amenity.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Pool")

    def test_create_amenity_empty_name(self):
        """
        Test creating an amenity with an empty name should raise a ValueError.
        """
        with self.assertRaises(ValueError):
            Amenity(name="")

    def test_create_amenity_name_too_long(self):
        """
        Test creating an amenity with a name longer than 50 characters should raise a ValueError.
        """
        long_name = "a" * 51
        with self.assertRaises(ValueError):
            Amenity(name=long_name)

if __name__ == "__main__":
    unittest.main()
