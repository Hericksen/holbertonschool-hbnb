from user import User

def test_user_creation():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.is_admin is False  # Default value
    print({user.first_name})
    print({user.last_name})
    print({user.email})
    print({user.is_admin})

    print("User creation test passed!")

test_user_creation()
