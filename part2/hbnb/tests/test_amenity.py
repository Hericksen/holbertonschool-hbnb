import unittest

from app.models.amenity import Amenity


class TestAmenity(unittest.TestCase):

    def test_valid_amenity_creation(self):
        """Teste la création d'une commodité valide."""
        amenity = Amenity("WiFi")
        self.assertEqual(amenity.name, "WiFi")

    def test_invalid_name_empty(self):
        """Teste si un nom vide déclenche une erreur."""
        with self.assertRaises(ValueError):
            Amenity("")

    def test_invalid_name_too_long(self):
        """Teste si un nom trop long déclenche une erreur."""
        with self.assertRaises(ValueError):
            Amenity("A" * 51)


if __name__ == '__main__':
    unittest.main()