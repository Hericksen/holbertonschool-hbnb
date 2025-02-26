from datetime import datetime
from user import User
from place import Place
from review import Review

def test_review_creation():
    """Test si une review est correctement créée"""
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
    place = Place(title="Appartement", description="Très cosy", price=120, latitude=48.8566, longitude=2.3522, owner=user)
    review = Review(text="Super séjour !", rating=5, place=place, user=user)

    assert review.text == "Super séjour !"
    assert review.rating == 5
    assert review.place == place
    assert review.user == user
    assert isinstance(review.created_at, datetime)
    assert isinstance(review.updated_at, datetime)

    print("test_review_creation réussi !")

def test_review_rating_bounds():
    """Test que la note est bien entre 1 et 5"""
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
    place = Place(title="Appartement", description="Très cosy", price=120, latitude=48.8566, longitude=2.3522, owner=user)
    review = Review(text="Super séjour !", rating=3, place=place, user=user)

    review.rating = 5
    assert review.rating == 5  # Devrait être limité à 5

    review.rating = 1
    assert review.rating == 1  # Devrait être limité à 1

    print("test_review_rating_bounds réussi !")

if __name__ == "__main__":
    test_review_creation()
    test_review_rating_bounds()
    print("Tous les tests sont passés avec succès !")
