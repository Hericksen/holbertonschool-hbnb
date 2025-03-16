from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity


def main():
    # Creating a user
    user1 = User(first_name="Alice", last_name="Smith",
                 email="alice@example.com")
    user2 = User(first_name="Bob", last_name="Johnson",
                 email="bob@example.com")

    # Creation of places
    place1 = Place(
        title="Cozy Apartment",
        description="Superb apartment in the city center",
        price=100.0,
        latitude=48.8566,
        longitude=2.3522,
        owner=user1
    )
    place2 = Place(
        title="Luxurious Villa",
        description="Villa with swimming pool",
        price=300.0,
        latitude=43.2965,
        longitude=5.3698,
        owner=user2
    )

    # User 1 owns place1
    user1.add_place(place1)
    # User 2 owns place2
    user2.add_place(place2)

    # Creation of amenities
    wifi = Amenity(name="Wi-Fi")
    parking = Amenity(name="Parking")

    # Add amenities
    place1.add_amenity(wifi)
    place1.add_amenity(parking)
    place2.add_amenity(wifi)

    # Creation of a review
    review1 = Review(text="Great stay !", rating=5, place=place1, user=user2)
    review2 = Review(text="Not bad at all", rating=4, place=place2, user=user1)

    # Added notice to both location and user
    place1.add_review(review1)
    user2.add_review(review1)

    place2.add_review(review2)
    user1.add_review(review2)

    # Displaying results
    print(f"The place '{place1.title}' has {len(place1.reviews)} notice.")
    print(
        f"the user {user2.first_name} has écrit {len(user2.reviews)} notice.")
    print(f"the user {user1.first_name} possède {len(user1.places)} place.")
    print(f"Le lieu '{place1.title}' has {len(place1.amenities)} amenities.")

    print(f"The place '{place2.title}' has {len(place2.reviews)} notice.")
    print(f"the user {user1.first_name} wrote {len(user1.reviews)} notice.")


if __name__ == "__main__":
    main()
