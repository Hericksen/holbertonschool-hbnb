import unittest
import uuid
from datetime import datetime
from app.models.base_model import BaseModel
import time


class TestBaseModel(unittest.TestCase):

    def test_instance_creation(self):
        """Test the creation of a BaseModel instance."""
        obj = BaseModel()
        self.assertIsInstance(obj, BaseModel)
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(uuid.UUID(obj.id), uuid.UUID)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_id(self):
        """Verifies that each instance has a unique ID."""
        obj1 = BaseModel()
        obj2 = BaseModel()
        self.assertNotEqual(obj1.id, obj2.id)

    def test_save_updates_timestamp(self):
        """Check that `save()` updates `updated_at`."""
        obj = BaseModel()
        old_updated_at = obj.updated_at
        time.sleep(1)  # Pause to ensure timestamp change
        obj.save()
        self.assertGreater(obj.updated_at, old_updated_at)

    def test_update_method(self):
        """Tests the update() method to modify attributes."""
        obj = BaseModel()
        old_updated_at = obj.updated_at
        obj.update(
            {"id": "test-id", "created_at": obj.created_at, "new_attr": "test"})

        # Checking for updates
        self.assertEqual(obj.id, "test-id")  # ID needs to be updated
        # Should not add new attributes
        self.assertFalse(hasattr(obj, "new_attr"))
        # `updated_at` needs to be updated
        self.assertGreater(obj.updated_at, old_updated_at)


if __name__ == '__main__':
    unittest.main()