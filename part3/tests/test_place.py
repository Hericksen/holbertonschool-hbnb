import unittest
from unittest import mock
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity


class TestPlace(unittest.TestCase):

    def test_valid_place_creation(self):
        """Tests the creation of a valid location."""
        owner_mock = mock.Mock(spec=User)
        place = Place("Cozy Cabin", "A small cozy cabin in the woods",
                      120.0, 45.0, -73.0, owner_mock)

        self.assertEqual(place.title, "Cozy Cabin")
        self.assertEqual(place.description, "A small cozy cabin in the woods")
        self.assertEqual(place.price, 120.0)
        self.assertEqual(place.latitude, 45.0)
        self.assertEqual(place.longitude, -73.0)
        self.assertEqual(place.owner, owner_mock)
        self.assertEqual(place.reviews, [])
        self.assertEqual(place.amenities, [])

    def test_invalid_title_empty(self):
        """Tests if an empty title triggers an error."""
        owner_mock = mock.Mock(spec=User)
        with self.assertRaises(ValueError):
            Place("", "Description", 50.0, 40.0, -75.0, owner_mock)

    def test_invalid_title_too_long(self):
        """Tests if a title that is too long triggers an error."""
        owner_mock = mock.Mock(spec=User)
        with self.assertRaises(ValueError):
            Place("T" * 101, "Description", 50.0, 40.0, -75.0, owner_mock)

    def test_invalid_price_negative(self):
        """Tests if a negative price triggers an error."""
        owner_mock = mock.Mock(spec=User)
        with self.assertRaises(ValueError):
            Place("Nice Place", "Description", -10.0, 40.0, -75.0, owner_mock)

    def test_invalid_latitude_out_of_bounds(self):
        """Tests if out of range latitude triggers an error."""
        owner_mock = mock.Mock(spec=User)
        with self.assertRaises(ValueError):
            Place("Nice Place", "Description", 100.0, -91.0, -75.0, owner_mock)

    def test_invalid_longitude_out_of_bounds(self):
        """Tests if longitude out of range triggers an error."""
        owner_mock = mock.Mock(spec=User)
        with self.assertRaises(ValueError):
            Place("Nice Place", "Description", 100.0, 40.0, 181.0, owner_mock)

    def test_invalid_owner_type(self):
        """Test if wrong type for owner triggers an error."""
        with self.assertRaises(TypeError):
            Place("Nice Place", "Description", 100.0,
                  40.0, -75.0, "not_a_user_instance")

    def test_add_review(self):
        """Test adding a review to a location."""
        owner_mock = mock.Mock(spec=User)
        review_mock = mock.Mock(spec=Review)
        place = Place("Nice Place", "Description",
                      100.0, 40.0, -75.0, owner_mock)

        place.add_review(review_mock)
        self.assertIn(review_mock, place.reviews)

    def test_add_review_invalid_type(self):
        """Test if the wrong review type triggers an error."""
        owner_mock = mock.Mock(spec=User)
        place = Place("Nice Place", "Description",
                      100.0, 40.0, -75.0, owner_mock)

        with self.assertRaises(TypeError):
            place.add_review("not_a_review_instance")

    def test_add_amenity(self):
        """Test adding an amenity to a location."""
        owner_mock = mock.Mock(spec=User)
        amenity_mock = mock.Mock(spec=Amenity)
        place = Place("Nice Place", "Description",
                      100.0, 40.0, -75.0, owner_mock)

        place.add_amenity(amenity_mock)
        self.assertIn(amenity_mock, place.amenities)

    def test_add_amenity_invalid_type(self):
        """Tests if the wrong convenience type triggers an error."""
        owner_mock = mock.Mock(spec=User)
        place = Place("Nice Place", "Description",
                      100.0, 40.0, -75.0, owner_mock)

        with self.assertRaises(TypeError):
            place.add_amenity("not_an_amenity_instance")


if __name__ == '__main__':
    unittest.main()