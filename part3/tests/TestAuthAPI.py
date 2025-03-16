import unittest
import json
import uuid
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import decode_token

class AuthAPITestCase(unittest.TestCase):
    """
    This test case verifies the authentication endpoints:
    - POST /login
    - GET /protected
    under the assumption that the namespace is registered at '/api/v1/auth'.
    """

    def setUp(self):
        """
        Set up a test application context and an in-memory database.
        Create a user with known credentials for login tests.
        """
        self.app = create_app("config.TestConfig")  # Ensure TestConfig is defined
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clear any existing emails to avoid collisions
        User.existing_emails.clear()

        # Create a user for login tests
        self.test_email = f"{uuid.uuid4()}@example.com"
        self.test_password = "correct_password"
        self.user = User(
            first_name="Login",
            last_name="Tester",
            email=self.test_email,
            password=self.test_password,
            is_admin=False
        )
        db.session.add(self.user)
        db.session.commit()

        self.client = self.app.test_client()

        # Base URL for auth endpoints
        # e.g. api.add_namespace(auth_ns, path='/api/v1/auth')
        self.base_url = "/api/v1/auth"

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        """
        Test logging in with valid credentials returns a 200 status
        and provides an access_token.
        """
        data = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = self.client.post(
            f"{self.base_url}/login",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.data)
        self.assertIn("access_token", resp_json)
        self.assertIn("token_type", resp_json)
        self.assertEqual(resp_json["token_type"], "Bearer")

        # Optionally decode the token to verify the claims
        token_data = decode_token(resp_json["access_token"])
        self.assertEqual(token_data["sub"]["id"], self.user.id)
        self.assertFalse(token_data["sub"]["is_admin"])

    def test_login_invalid_credentials(self):
        """
        Test logging in with invalid credentials returns a 401 status.
        """
        data = {
            "email": self.test_email,
            "password": "wrong_password"
        }
        response = self.client.post(
            f"{self.base_url}/login",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        resp_json = json.loads(response.data)
        self.assertIn("message", resp_json)
        self.assertEqual(resp_json["message"], "Invalid credentials")

    def test_protected_with_valid_token(self):
        """
        Test accessing the protected endpoint with a valid JWT token returns 200.
        """
        # First, login to get a valid token
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        login_resp = self.client.post(
            f"{self.base_url}/login",
            data=json.dumps(login_data),
            content_type="application/json"
        )
        token = json.loads(login_resp.data)["access_token"]

        # Access the protected route
        response = self.client.get(
            f"{self.base_url}/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.data)
        self.assertIn("message", resp_json)
        # "Hello, user <user_id>"
        self.assertIn(f"Hello, user {self.user.id}", resp_json["message"])

    def test_protected_no_token(self):
        """
        Test accessing the protected endpoint without providing a token returns 401.
        """
        response = self.client.get(f"{self.base_url}/protected")
        self.assertEqual(response.status_code, 401)
        resp_json = json.loads(response.data)
        self.assertIn("msg", resp_json)
        self.assertIn("Missing Authorization Header", resp_json["msg"])

    def test_protected_invalid_token(self):
        """
        Test accessing the protected endpoint with an invalid token returns 422 or 401.
        """
        # Provide a malformed token
        response = self.client.get(
            f"{self.base_url}/protected",
            headers={"Authorization": "Bearer invalid.token.value"}
        )
        # Depending on your JWT settings, it could be 422 or 401
        self.assertIn(response.status_code, [401, 422])
        resp_json = json.loads(response.data)
        self.assertIn("msg", resp_json)

if __name__ == "__main__":
    unittest.main()
