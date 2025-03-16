import unittest
import json
import uuid
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token
from config import DevelopmentConfig

class UserAPITestCase(unittest.TestCase):
    """
    This test case verifies the User API endpoints, including creation, retrieval,
    update, and deletion of users. It also checks that only the user themselves
    or an admin can update/delete a user, and that only an admin can retrieve
    the list of all users.
    """

    def setUp(self):
        """
        Set up a test application context and an in-memory database.
        Create test users: a normal user, a second user, and an admin user.
        """
        self.app = create_app("config.TestConfig")  # Ensure TestConfig is defined
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear any existing emails to avoid collisions
        User.existing_emails.clear()

        # Create a normal user
        user1_email = f"{uuid.uuid4()}@example.com"
        self.user1 = User(
            first_name="User1",
            last_name="Normal",
            email=user1_email,
            password="user1pass",
            is_admin=False
        )
        db.session.add(self.user1)
        db.session.commit()

        # Create a second user
        user2_email = f"{uuid.uuid4()}@example.com"
        self.user2 = User(
            first_name="User2",
            last_name="Normal",
            email=user2_email,
            password="user2pass",
            is_admin=False
        )
        db.session.add(self.user2)
        db.session.commit()

        # Create an admin user
        admin_email = f"{uuid.uuid4()}@example.com"
        self.admin_user = User(
            first_name="Admin",
            last_name="User",
            email=admin_email,
            password="adminpass",
            is_admin=True
        )
        db.session.add(self.admin_user)
        db.session.commit()

        # Generate JWT tokens for each user
        with self.app.test_request_context():
            self.user1_token = create_access_token(identity={"id": self.user1.id, "is_admin": self.user1.is_admin})
            self.user2_token = create_access_token(identity={"id": self.user2.id, "is_admin": self.user2.is_admin})
            self.admin_token = create_access_token(identity={"id": self.admin_user.id, "is_admin": self.admin_user.is_admin})

        self.client = self.app.test_client()
        # Assume the namespace is registered under /api/v1/users
        self.base_url = "/api/v1/users"

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ------------------ TEST: CREATE USER (POST /users) ------------------

    def test_create_user_admin_secret(self):
        """
        Test creating a user with the correct admin_secret should make the user an admin.
        """
        data = {
            "first_name": "Secret",
            "last_name": "Admin",
            "email": f"{uuid.uuid4()}@example.com",
            "password": "secretpass",
            "admin_secret": DevelopmentConfig.ADMIN_SECRET
        }
        response = self.client.post(
            f"{self.base_url}/",
            json=data
        )
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertTrue(resp_json["is_admin"])

    def test_create_user_duplicate_email(self):
        """
        Test creating a user with an existing email should return 400.
        """
        data = {
            "first_name": "Dup",
            "last_name": "Email",
            "email": self.user1.email,  # same as existing user1
            "password": "dupPass"
        }
        response = self.client.post(
            f"{self.base_url}/",
            json=data
        )
        self.assertEqual(response.status_code, 400)

    # ------------------ TEST: GET ALL USERS (GET /users) ------------------

    def test_get_all_users_not_admin(self):
        """
        Test that a non-admin user cannot retrieve the list of all users (403).
        """
        response = self.client.get(
            f"{self.base_url}/",
            headers={"Authorization": f"Bearer {self.user1_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_get_all_users_admin(self):
        """
        Test that an admin can retrieve the list of all users.
        """
        response = self.client.get(
            f"{self.base_url}/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertIsInstance(resp_json, list)
        self.assertGreaterEqual(len(resp_json), 3)

    # ------------------ TEST: GET USER BY ID (GET /users/<user_id>) ------------------

    def test_get_user_by_id_success(self):
        """
        Test retrieving a user by their ID.
        """
        response = self.client.get(f"{self.base_url}/{self.user1.id}")
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json["id"], self.user1.id)
        self.assertEqual(resp_json["email"], self.user1.email)

    def test_get_user_not_found(self):
        """
        Test retrieving a non-existent user returns 404.
        """
        response = self.client.get(f"{self.base_url}/nonexistent-id")
        self.assertEqual(response.status_code, 404)

    # ------------------ TEST: UPDATE USER (PUT /users/<user_id>) ------------------

    def test_update_user_self(self):
        """
        Test that a user can update their own details.
        """
        update_data = {
            "first_name": "UpdatedName",
            "password": "newpass123"
        }
        response = self.client.put(
            f"{self.base_url}/{self.user1.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.user1_token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json["first_name"], "UpdatedName")

    def test_update_user_admin(self):
        """
        Test that an admin can update another user's details.
        """
        update_data = {
            "first_name": "AdminUpdated",
        }
        response = self.client.put(
            f"{self.base_url}/{self.user1.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json["first_name"], "AdminUpdated")

    def test_update_user_unauthorized(self):
        """
        Test that a user cannot update someone else's account unless they are admin.
        """
        update_data = {
            "first_name": "HackerUpdate"
        }
        response = self.client.put(
            f"{self.base_url}/{self.user2.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.user1_token}"}
        )
        self.assertEqual(response.status_code, 403)

    # ------------------ TEST: DELETE USER (DELETE /users/<user_id>) ------------------

    def test_delete_user_self(self):
        """
        Test that a user can delete their own account.
        """
        response = self.client.delete(
            f"{self.base_url}/{self.user1.id}",
            headers={"Authorization": f"Bearer {self.user1_token}"}
        )
        self.assertEqual(response.status_code, 200)
        # Check that the user is no longer found
        get_resp = self.client.get(f"{self.base_url}/{self.user1.id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_user_admin(self):
        """
        Test that an admin can delete another user's account.
        """
        response = self.client.delete(
            f"{self.base_url}/{self.user2.id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        # Verify user2 is deleted
        get_resp = self.client.get(f"{self.base_url}/{self.user2.id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_user_unauthorized(self):
        """
        Test that a user cannot delete someone else's account unless they are admin.
        """
        response = self.client.delete(
            f"{self.base_url}/{self.user2.id}",
            headers={"Authorization": f"Bearer {self.user1_token}"}
        )
        self.assertEqual(response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
