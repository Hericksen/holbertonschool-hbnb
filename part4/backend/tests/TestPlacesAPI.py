import unittest
import json
import uuid
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token

class PlaceAPITestCase(unittest.TestCase):
    """
    This test case verifies the Place API endpoints, including creation,
    retrieval, update, and deletion of places. It also checks that only
    the owner or an admin can update/delete a place.
    """

    def setUp(self):
        """
        Set up a test application context and an in-memory database.
        Create test users: an owner, a non-owner, and an admin.
        """
        self.app = create_app("config.TestConfig")  # Make sure TestConfig is defined
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear any existing emails to avoid collisions
        User.existing_emails.clear()

        # Create an owner user (non-admin)
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

        # Create a non-owner user (non-admin)
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
        # Adapt this if your namespace is registered differently:
        # api.add_namespace(places_ns, path='/api/v1/places')
        self.base_url = "/api/v1/places"

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_place_success(self):
        """
        Test creating a place with valid data using the owner's token.
        """
        data = {
            "title": "Cozy Cottage",
            "description": "A lovely place to stay",
            "price": 120.0,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        response = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertIn("id", resp_json)
        self.assertEqual(resp_json["title"], "Cozy Cottage")
        self.assertEqual(resp_json["owner"]["id"], self.owner.id)

    def test_create_place_invalid_price(self):
        """
        Test creating a place with a negative price should return 400.
        """
        data = {
            "title": "Invalid Price Place",
            "description": "Price is negative",
            "price": -50,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        response = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_places(self):
        """
        Test retrieving a list of all places.
        """
        # Create two places
        data1 = {
            "title": "Place One",
            "description": "First place",
            "price": 100,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        data2 = {
            "title": "Place Two",
            "description": "Second place",
            "price": 150,
            "latitude": 46.0,
            "longitude": 11.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        self.client.post(
            f"{self.base_url}/",
            json=data1,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.client.post(
            f"{self.base_url}/",
            json=data2,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )

        response = self.client.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertIsInstance(resp_json, list)
        self.assertGreaterEqual(len(resp_json), 2)

    def test_get_place_by_id(self):
        """
        Test retrieving a specific place by its ID.
        """
        data = {
            "title": "Unique Place",
            "description": "Special place",
            "price": 200,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        place_id = post_resp.get_json()["id"]

        response = self.client.get(f"{self.base_url}/{place_id}")
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json["id"], place_id)
        self.assertEqual(resp_json["title"], "Unique Place")

    def test_update_place_success(self):
        """
        Test updating a place with valid data using the owner's token.
        """
        data = {
            "title": "Old Title",
            "description": "Old desc",
            "price": 80,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        place_id = post_resp.get_json()["id"]

        updated_data = {
            "title": "New Title",
            "price": 95
        }
        response = self.client.put(
            f"{self.base_url}/{place_id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json["title"], "New Title")
        self.assertEqual(resp_json["price"], 95)


    def test_delete_place_non_owner(self):
        """
        Test that a non-owner (and non-admin) cannot delete a place.
        """
        data = {
            "title": "Protected Place",
            "description": "Owner only",
            "price": 70,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        place_id = post_resp.get_json()["id"]

        response = self.client.delete(
            f"{self.base_url}/{place_id}",
            headers={"Authorization": f"Bearer {self.non_owner_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_place_admin(self):
        """
        Test that an admin can delete any place.
        """
        data = {
            "title": "Admin Deletion Place",
            "description": "Should be removed by admin",
            "price": 70,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        place_id = post_resp.get_json()["id"]

        response = self.client.delete(
            f"{self.base_url}/{place_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
