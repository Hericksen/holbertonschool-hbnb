import unittest
import json
import uuid
from app import create_app, db
from app.models.user import User
from app.models.amenity import Amenity
from flask_jwt_extended import create_access_token

class AmenityAPITestCase(unittest.TestCase):
    """
    This test case verifies the Amenity API endpoints, assuming that
    the namespace is registered with a path like '/api/v1/amenities'.
    It covers creation, retrieval, update, and deletion of amenities,
    including authorization based on the owner or admin role.
    """

    def setUp(self):
        """
        Set up a test application context and an in-memory database.
        Create test users (one owner, one non-owner, and one admin).
        """
        self.app = create_app("config.TestConfig")  # Ensure TestConfig is defined
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear any existing emails to avoid duplicate email errors
        User.existing_emails.clear()

        # Create a user who will be the owner of amenities (non-admin)
        owner_email = f"{uuid.uuid4()}@example.com"
        self.owner = User(
            first_name="Owner",
            last_name="User",
            email=owner_email,
            password="ownerpass",
            is_admin=False
        )
        db.session.add(self.owner)
        db.session.commit()

        # Create a second user (non-owner, non-admin)
        non_owner_email = f"{uuid.uuid4()}@example.com"
        self.non_owner = User(
            first_name="NonOwner",
            last_name="User",
            email=non_owner_email,
            password="nonownerpass",
            is_admin=False
        )
        db.session.add(self.non_owner)
        db.session.commit()

        # Create an admin user
        admin_email = f"{uuid.uuid4()}@example.com"
        self.admin = User(
            first_name="Admin",
            last_name="User",
            email=admin_email,
            password="adminpass",
            is_admin=True
        )
        db.session.add(self.admin)
        db.session.commit()

        # Generate JWT tokens for each user
        with self.app.test_request_context():
            self.owner_token = create_access_token(identity={"id": self.owner.id, "is_admin": self.owner.is_admin})
            self.non_owner_token = create_access_token(identity={"id": self.non_owner.id, "is_admin": self.non_owner.is_admin})
            self.admin_token = create_access_token(identity={"id": self.admin.id, "is_admin": self.admin.is_admin})

        self.client = self.app.test_client()

        # Base URL for amenities, assuming namespace is added as:
        # api.add_namespace(amenities_ns, path='/api/v1/amenities')
        self.base_url = "/api/v1/amenities"

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_amenity_success(self):
        """
        Test creating an amenity with valid data, using the owner's token.
        """
        data = {"name": "Pool"}
        response = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 201)
        resp_json = json.loads(response.data)
        self.assertIn("id", resp_json)
        self.assertEqual(resp_json["name"], "Pool")

    def test_create_amenity_invalid_name(self):
        """
        Test creating an amenity with an empty name should return 400.
        """
        data = {"name": ""}
        response = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_amenities(self):
        """
        Test retrieving all amenities.
        """
        # Create two amenities
        data1 = {"name": "Gym"}
        data2 = {"name": "Sauna"}
        self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data1),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data2),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )

        # Now, GET the amenities list
        response = self.client.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.data)
        self.assertTrue(isinstance(resp_json, list))
        self.assertGreaterEqual(len(resp_json), 2)

    def test_get_amenity_by_id(self):
        """
        Test retrieving a single amenity by its ID.
        """
        data = {"name": "Library"}
        post_resp = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        amenity_id = json.loads(post_resp.data)["id"]

        response = self.client.get(f"{self.base_url}/{amenity_id}")
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.data)
        self.assertEqual(resp_json["id"], amenity_id)
        self.assertEqual(resp_json["name"], "Library")

    def test_update_amenity_success(self):
        """
        Test updating an amenity's information.
        """
        # Create an amenity
        data = {"name": "Old Name"}
        post_resp = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        amenity_id = json.loads(post_resp.data)["id"]

        # Update the amenity
        updated_data = {"name": "New Name"}
        response = self.client.put(
            f"{self.base_url}/{amenity_id}",
            data=json.dumps(updated_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.data)
        self.assertEqual(resp_json["name"], "New Name")

    def test_update_amenity_not_found(self):
        """
        Test updating an amenity that does not exist returns 404.
        """
        updated_data = {"name": "Doesn't Matter"}
        response = self.client.put(
            f"{self.base_url}/nonexistent-id",
            data=json.dumps(updated_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_amenity_owner(self):
        """
        Test that the owner of an amenity can delete it.
        """
        data = {"name": "ToDelete"}
        post_resp = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        amenity_id = json.loads(post_resp.data)["id"]

        response = self.client.delete(
            f"{self.base_url}/{amenity_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_amenity_non_owner(self):
        """
        Test that a non-owner (and non-admin) cannot delete an amenity.
        """
        data = {"name": "NoDelete"}
        post_resp = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        amenity_id = json.loads(post_resp.data)["id"]

        response = self.client.delete(
            f"{self.base_url}/{amenity_id}",
            headers={"Authorization": f"Bearer {self.non_owner_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_amenity_admin(self):
        """
        Test that an admin can delete any amenity.
        """
        data = {"name": "AdminDelete"}
        post_resp = self.client.post(
            f"{self.base_url}/",
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        amenity_id = json.loads(post_resp.data)["id"]

        response = self.client.delete(
            f"{self.base_url}/{amenity_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
