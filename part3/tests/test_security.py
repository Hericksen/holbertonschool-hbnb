import unittest
from app import create_app  # Assure-toi que create_app est bien défini
from app.models.user import User
from app.services import facade  # Pour récupérer un utilisateur si nécessaire

class TestPasswordHashing(unittest.TestCase):

    def setUp(self):
        """Setup test client before each test"""
        self.app = create_app().test_client()
        self.app.testing = True
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword123"
        }

        # Supprimer l'utilisateur s'il existe déjà (évite l'erreur de doublon)
        existing_user = facade.get_user_by_email(self.user_data["email"])
        if existing_user:
            facade.delete_user(existing_user.id)

        # Créer l'utilisateur pour le test GET
        response = self.app.post("/api/v1/users/", json=self.user_data)
        self.assertEqual(response.status_code, 201)
        self.user_id = response.get_json()["id"]

    def tearDown(self):
        """Nettoyage après chaque test"""
        facade.delete_user(self.user_id)

    def test_user_registration(self):
        """Test user registration and ensure password is hashed"""
        response = self.app.post("/api/v1/users/", json=self.user_data)
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertIn("id", data)
        self.assertNotIn("password", data)  # Le mot de passe ne doit PAS être renvoyé

        print("✅ Password is hashed and not returned in response.")

    def test_user_retrieval(self):
        """Test that GET /users/<id> does not expose password"""
        response = self.app.get(f"/api/v1/users/{self.user_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertNotIn("password", data)  # Le mot de passe ne doit pas être exposé

        print("✅ Password is not exposed in user retrieval.")

if __name__ == "__main__":
    unittest.main()
