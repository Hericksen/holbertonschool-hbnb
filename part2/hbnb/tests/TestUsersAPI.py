import unittest
import json
import uuid
from app import create_app
from app.models.user import User


class TestUsersAPI(unittest.TestCase):
    def setUp(self):
        """
        Before each test:
        - Remove all emails (if the User class manages uniqueness via a set).
        - Initialize the application in test mode.
        """
        User.existing_emails.clear()

        self.app = create_app()
        self.client = self.app.test_client()

    def test_create_user_valid(self):
        """
        Test for creating a valid user (all required fields).
        """
        random_email = f"user_{uuid.uuid4()}@example.com"
        payload = {
            "first_name": "Bob",
            "last_name": "Marley",
            "email": random_email
        }
        resp = self.client.post('/api/v1/users/', json=payload)
        self.assertEqual(resp.status_code, 201, msg=resp.data)
        data = json.loads(resp.data)
        self.assertIn("id", data)
        self.assertEqual(data["first_name"], "Bob")
        self.assertEqual(data["last_name"], "Marley")
        self.assertEqual(data["email"], random_email)

    def test_create_user_missing_required_field(self):
        """
        Test: omit a required field (e.g., 'email') => 400 Bad Request.
        """
        payload = {
            "first_name": "Charlie",
            "last_name": "Brown"
            # pas de "email"
        }
        resp = self.client.post('/api/v1/users/', json=payload)
        # Flask-RESTx should return 400 for a missing required field.
        self.assertEqual(resp.status_code, 400, msg=resp.data)

    def test_create_user_duplicate_email(self):
        """
        Test for creating a user with an already used email => 400
        and the message 'Email already registered'.
        """
        email = f"duplicate_{uuid.uuid4()}@example.com"
        # Create for 1st time
        payload1 = {
            "first_name": "Alice",
            "last_name": "Doe",
            "email": email
        }
        resp1 = self.client.post('/api/v1/users/', json=payload1)
        self.assertEqual(resp1.status_code, 201, msg=resp1.data)

        # Try to create with same email
        payload2 = {
            "first_name": "Alice2",
            "last_name": "Doe2",
            "email": email
        }
        resp2 = self.client.post('/api/v1/users/', json=payload2)
        self.assertEqual(resp2.status_code, 400, msg=resp2.data)
        data = json.loads(resp2.data)
        # On vérifie le message
        self.assertIn("Email already registered", json.dumps(data))

    def test_get_user_valid(self):
        """
        Create a user, then GET user with id => 200 OK.
        """
        random_email = f"user_{uuid.uuid4()}@example.com"
        create_payload = {
            "first_name": "John",
            "last_name": "Lennon",
            "email": random_email
        }
        create_resp = self.client.post('/api/v1/users/', json=create_payload)
        self.assertEqual(create_resp.status_code, 201, msg=create_resp.data)
        user_data = json.loads(create_resp.data)
        user_id = user_data["id"]

        # Retrieve user
        get_resp = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(get_resp.status_code, 200, msg=get_resp.data)
        fetched_data = json.loads(get_resp.data)
        self.assertEqual(fetched_data["id"], user_id)
        self.assertEqual(fetched_data["email"], random_email)

    def test_get_user_not_found(self):
        """
        Trying to get user with non existant ID => 404.
        """
        get_resp = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(get_resp.status_code, 404, msg=get_resp.data)
        data = json.loads(get_resp.data)
        self.assertIn("User not found", json.dumps(data))


if __name__ == "__main__":
    unittest.main()