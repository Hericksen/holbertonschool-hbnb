import unittest
import json
import uuid
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token

class ReviewAPITestCase(unittest.TestCase):
    """
    This test case verifies the Review API endpoints, including creation,
    retrieval, update, and deletion of reviews. It also checks that only
    the author or an admin can update/delete a review.
    """

    def setUp(self):
        """
        Set up a test application context and an in-memory database.
        Create test users (an owner, a non-owner, and an admin).
        Create a place so that we can attach reviews to it.
        """
        self.app = create_app("config.TestConfig")  # Assure-toi que TestConfig est défini
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Vider les emails existants pour éviter les collisions
        User.existing_emails.clear()

        # Créer un utilisateur "owner" (non-admin)
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

        # Créer un utilisateur "non_owner" (non-admin)
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

        # Créer un utilisateur admin
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

        # Générer des tokens JWT pour chaque utilisateur
        with self.app.test_request_context():
            self.owner_token = create_access_token(identity={"id": self.owner.id, "is_admin": self.owner.is_admin})
            self.non_owner_token = create_access_token(identity={"id": self.non_owner.id, "is_admin": self.non_owner.is_admin})
            self.admin_token = create_access_token(identity={"id": self.admin.id, "is_admin": self.admin.is_admin})

        # Créer un client de test
        self.client = self.app.test_client()

        # Chemin de base pour les reviews (en supposant que le namespace est enregistré sous /api/v1/reviews)
        self.base_url = "/api/v1/reviews"

        # Nous avons besoin d'un place pour pouvoir créer des reviews
        # On va appeler l'endpoint /api/v1/places pour en créer un via l'utilisateur owner
        self.place_base_url = "/api/v1/places"
        place_data = {
            "title": "Reviewable Place",
            "description": "A place to review",
            "price": 100,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": self.owner.id,
            "amenities": []
        }
        place_resp = self.client.post(
            f"{self.place_base_url}/",
            json=place_data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(place_resp.status_code, 201, "Failed to create a place in setUp")
        self.place_id = place_resp.get_json()["id"]

    def tearDown(self):
        """
        Remove the session and drop all tables after each test.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_review_success(self):
        """
        Test creating a review with valid data.
        The user is automatically set as the author from the JWT.
        """
        data = {
            "text": "Great place!",
            "rating": 5,
            "place_id": self.place_id
        }
        response = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertIn("id", resp_json)
        self.assertEqual(resp_json["text"], "Great place!")
        self.assertEqual(resp_json["rating"], 5)
        self.assertEqual(resp_json["place_id"], self.place_id)
        self.assertEqual(resp_json["user_id"], self.owner.id)

    def test_create_review_invalid_data(self):
        """
        Test creating a review with missing fields or invalid rating should return 400.
        """
        # Missing place_id
        data_missing = {
            "text": "No place ID",
            "rating": 4
        }
        resp_missing = self.client.post(
            f"{self.base_url}/",
            json=data_missing,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(resp_missing.status_code, 400)

        # Rating out of range
        data_bad_rating = {
            "text": "Bad rating",
            "rating": 6,
            "place_id": self.place_id
        }
        resp_bad_rating = self.client.post(
            f"{self.base_url}/",
            json=data_bad_rating,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(resp_bad_rating.status_code, 400)

    def test_get_all_reviews(self):
        """
        Test retrieving a list of all reviews.
        """
        # Créer deux reviews
        data1 = {"text": "Review One", "rating": 4, "place_id": self.place_id}
        data2 = {"text": "Review Two", "rating": 5, "place_id": self.place_id}
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

        resp = self.client.get(f"{self.base_url}/")
        self.assertEqual(resp.status_code, 200)
        reviews_list = resp.get_json()
        self.assertIsInstance(reviews_list, list)
        self.assertGreaterEqual(len(reviews_list), 2)

    def test_get_review_by_id(self):
        """
        Test retrieving a review by its ID.
        """
        data = {"text": "Unique Review", "rating": 5, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        resp = self.client.get(f"{self.base_url}/{review_id}")
        self.assertEqual(resp.status_code, 200)
        review_json = resp.get_json()
        self.assertEqual(review_json["id"], review_id)
        self.assertEqual(review_json["text"], "Unique Review")

    def test_get_review_not_found(self):
        """
        Test retrieving a non-existent review should return 404.
        """
        resp = self.client.get(f"{self.base_url}/nonexistent-id")
        self.assertEqual(resp.status_code, 404)

    def test_update_review_success(self):
        """
        Test updating an existing review by its author.
        """
        # Créer une review
        data = {"text": "Old text", "rating": 3, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        updated_data = {"text": "Updated text", "rating": 4}
        resp_update = self.client.put(
            f"{self.base_url}/{review_id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(resp_update.status_code, 200)
        review_json = resp_update.get_json()
        self.assertEqual(review_json["text"], "Updated text")
        self.assertEqual(review_json["rating"], 4)

    def test_update_review_unauthorized(self):
        """
        Test that a non-author (and non-admin) cannot update a review.
        """
        # Créer une review avec l'owner
        data = {"text": "Owner's review", "rating": 3, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        updated_data = {"text": "Hacked review", "rating": 5}
        resp_update = self.client.put(
            f"{self.base_url}/{review_id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {self.non_owner_token}"}
        )
        self.assertEqual(resp_update.status_code, 403)

    def test_delete_review_author(self):
        """
        Test that the author of the review can delete it.
        """
        data = {"text": "Will be deleted", "rating": 2, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        resp_delete = self.client.delete(
            f"{self.base_url}/{review_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        self.assertEqual(resp_delete.status_code, 200)

    def test_delete_review_non_author(self):
        """
        Test that a non-author (and non-admin) cannot delete a review.
        """
        data = {"text": "Protected review", "rating": 3, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        resp_delete = self.client.delete(
            f"{self.base_url}/{review_id}",
            headers={"Authorization": f"Bearer {self.non_owner_token}"}
        )
        self.assertEqual(resp_delete.status_code, 403)

    def test_delete_review_admin(self):
        """
        Test that an admin can delete any review.
        """
        data = {"text": "Admin deletion", "rating": 5, "place_id": self.place_id}
        post_resp = self.client.post(
            f"{self.base_url}/",
            json=data,
            headers={"Authorization": f"Bearer {self.owner_token}"}
        )
        review_id = post_resp.get_json()["id"]

        resp_delete = self.client.delete(
            f"{self.base_url}/{review_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(resp_delete.status_code, 200)


if __name__ == "__main__":
    unittest.main()
