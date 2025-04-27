import unittest
import uuid
import time
from datetime import datetime
from app import create_app, db
from app.models.BaseModel import BaseModel

# A dummy model for testing BaseModel functionality.
class DummyModel(BaseModel):
    __tablename__ = 'dummy'
    dummy_field = db.Column(db.String(50), nullable=True)
    another_field = db.Column(db.Integer, nullable=True)

    def __init__(self, dummy_field=None, another_field=None):
        super().__init__()
        self.dummy_field = dummy_field
        self.another_field = another_field

class BaseModelFullTestCase(unittest.TestCase):
    """
    This test case verifies the functionality of the BaseModel
    using a DummyModel that inherits from BaseModel.
    """

    def setUp(self):
        """
        Set up a test application context and create all tables
        in an in-memory database.
        """
        # Create the test app using the TestConfig (ensure it is defined)
        self.app = create_app("config.TestConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        Remove the database session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_id_is_uuid(self):
        """
        Test that a new DummyModel instance has an id that is a valid UUID string.
        """
        instance = DummyModel(dummy_field="test")
        db.session.add(instance)
        db.session.commit()
        self.assertIsNotNone(instance.id)
        try:
            uuid_obj = uuid.UUID(instance.id, version=4)
        except ValueError:
            self.fail("instance.id is not a valid UUID")

    def test_created_at_and_updated_at_initially_equal(self):
        """
        Test that created_at and updated_at are set and nearly equal upon creation.
        """
        instance = DummyModel(dummy_field="test")
        db.session.add(instance)
        db.session.commit()
        self.assertIsNotNone(instance.created_at)
        self.assertIsNotNone(instance.updated_at)
        self.assertAlmostEqual(
            instance.created_at.timestamp(),
            instance.updated_at.timestamp(),
            delta=1
        )

    def test_save_updates_updated_at(self):
        """
        Test that calling save() updates the updated_at timestamp.
        """
        instance = DummyModel(dummy_field="test")
        db.session.add(instance)
        db.session.commit()
        old_updated_at = instance.updated_at
        time.sleep(1)
        instance.save()
        db.session.commit()
        self.assertGreater(instance.updated_at, old_updated_at)

    def test_update_method_updates_fields(self):
        """
        Test that update() modifies attributes and updates the updated_at timestamp.
        """
        instance = DummyModel(dummy_field="initial", another_field=10)
        db.session.add(instance)
        db.session.commit()
        old_updated_at = instance.updated_at
        time.sleep(1)
        update_data = {"dummy_field": "changed", "another_field": 20}
        instance.update(update_data)
        db.session.commit()
        self.assertEqual(instance.dummy_field, "changed")
        self.assertEqual(instance.another_field, 20)
        self.assertGreater(instance.updated_at, old_updated_at)

    def test_update_method_ignores_nonexistent_field(self):
        """
        Test that update() ignores keys that are not attributes of the instance.
        """
        instance = DummyModel(dummy_field="initial")
        db.session.add(instance)
        db.session.commit()
        instance.update({"nonexistent_field": "value", "dummy_field": "updated"})
        db.session.commit()
        self.assertEqual(instance.dummy_field, "updated")
        self.assertNotIn("nonexistent_field", instance.__dict__)

    def test_update_method_with_empty_dict(self):
        """
        Test that update() with an empty dictionary still calls save(),
        resulting in an updated updated_at timestamp.
        """
        instance = DummyModel(dummy_field="test")
        db.session.add(instance)
        db.session.commit()
        old_updated_at = instance.updated_at
        time.sleep(1)
        instance.update({})
        db.session.commit()
        self.assertGreaterEqual(instance.updated_at, old_updated_at)

if __name__ == "__main__":
    unittest.main()
