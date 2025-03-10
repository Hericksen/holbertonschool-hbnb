import unittest
import json
import uuid
from app import create_app
from app.models.user import User


class TestPlacesAPI(unittest.TestCase):
    def setUp(self):

        User.existing_emails.clear()

        self.app = create_app()
        self.client = self.app.test_client()

        random_email = f"alice_{uuid.uuid4()}@example.com"

        user_payload = {
            "first_name": "Alice",
            "last_name": "Doe",
            "email": random_email
        }
        user_resp = self.client.post('/api/v1/users/', json=user_payload)
        self.assertEqual(user_resp.status_code, 201, msg=user_resp.data)
        user_data = json.loads(user_resp.data)
        self.user_id = user_data["id"]

        amenity_payload = {"name": "WiFi"}
        amenity_resp = self.client.post(
            '/api/v1/amenities/', json=amenity_payload)
        self.assertEqual(amenity_resp.status_code, 201, msg=amenity_resp.data)
        amenity_data = json.loads(amenity_resp.data)
        self.amenity_id = amenity_data["id"]

    def test_create_place_valid(self):
        payload = {
            "title": "Central Apartment",
            "description": "Nice place in city center",
            "price": 150.0,
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": self.user_id,
            "amenities": [self.amenity_id]
        }
        resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(resp.status_code, 201, msg=resp.data)
        data = json.loads(resp.data)
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Central Apartment")
        self.assertEqual(data["amenities"], ["WiFi"])

    def test_get_all_places(self):
        payload = {
            "title": "Apartment One",
            "description": "First apt",
            "price": 100.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        post_resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(post_resp.status_code, 201, msg=post_resp.data)

        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200, msg=resp.data)
        places_list = json.loads(resp.data)
        self.assertIsInstance(places_list, list)
        self.assertTrue(len(places_list) >= 1)

    def test_get_place_by_id(self):
        payload = {
            "title": "Test Place",
            "description": "A test place",
            "price": 120.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        post_resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(post_resp.status_code, 201, msg=post_resp.data)
        place_data = json.loads(post_resp.data)
        place_id = place_data["id"]

        get_resp = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(get_resp.status_code, 200, msg=get_resp.data)
        place_info = json.loads(get_resp.data)
        self.assertEqual(place_info["id"], place_id)
        self.assertEqual(place_info["title"], "Test Place")

    def test_get_place_not_found(self):

        get_resp = self.client.get('/api/v1/places/nonexistent-id')
        self.assertEqual(get_resp.status_code, 404, msg=get_resp.data)
        data = json.loads(get_resp.data)
        self.assertIn("Place not found", data.get("message", ""))

    def test_update_place_valid(self):
        payload = {
            "title": "Old Title",
            "description": "Old desc",
            "price": 100.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        post_resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(post_resp.status_code, 201, msg=post_resp.data)
        place_data = json.loads(post_resp.data)
        place_id = place_data["id"]

        update_payload = {
            "title": "New Title",
            "description": "New desc",
            "price": 120.0,
            "latitude": 49.0,
            "longitude": 3.0,
            "owner_id": self.user_id,
            "amenities": [self.amenity_id]
        }
        put_resp = self.client.put(
            f'/api/v1/places/{place_id}', json=update_payload)
        self.assertEqual(put_resp.status_code, 200, msg=put_resp.data)
        updated_data = json.loads(put_resp.data)
        self.assertEqual(updated_data["title"], "New Title")
        self.assertEqual(updated_data["description"], "New desc")
        self.assertEqual(updated_data["price"], 120.0)
        self.assertEqual(updated_data["latitude"], 49.0)
        self.assertEqual(updated_data["longitude"], 3.0)
        self.assertEqual(updated_data["amenities"], [self.amenity_id])

    def test_update_place_invalid_price(self):
        payload = {
            "title": "Place to update",
            "description": "desc",
            "price": 150.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        post_resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(post_resp.status_code, 201, msg=post_resp.data)
        place_data = json.loads(post_resp.data)
        place_id = place_data["id"]

        update_payload = {
            "price": -50.0,
            "title": "New Title",
            "description": "Should fail",
            "latitude": 49.0,
            "longitude": 3.0,
            "owner_id": self.user_id,
            "amenities": []
        }
        put_resp = self.client.put(
            f'/api/v1/places/{place_id}', json=update_payload)
        self.assertEqual(put_resp.status_code, 400, msg=put_resp.data)
        data = json.loads(put_resp.data)
        self.assertIn("non-negative", data["message"])

    def test_update_place_not_found(self):

        update_payload = {
            "title": "New Title",
            "price": 120.0,
            "amenities": []
        }
        put_resp = self.client.put(
            '/api/v1/places/nonexistent-id', json=update_payload)
        self.assertEqual(put_resp.status_code, 404, msg=put_resp.data)

    def test_update_place_invalid_owner(self):
        """
        Test update with invalide owner_id (inexistant user).
        """
        payload = {
            "title": "Place with Valid Owner",
            "description": "desc",
            "price": 150.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": self.user_id,
            "amenities": []
        }
        post_resp = self.client.post('/api/v1/places/', json=payload)
        self.assertEqual(post_resp.status_code, 201, msg=post_resp.data)
        place_data = json.loads(post_resp.data)
        place_id = place_data["id"]

        update_payload = {
            "owner_id": "invalid-owner-id",
            "title": "Updated Title",
            "amenities": []
        }
        put_resp = self.client.put(
            f'/api/v1/places/{place_id}', json=update_payload)
        self.assertEqual(put_resp.status_code, 400, msg=put_resp.data)
        data = json.loads(put_resp.data)
        self.assertIn("Owner not found", data["message"])


if __name__ == "__main__":
    unittest.main()