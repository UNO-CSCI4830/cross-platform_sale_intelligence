from backend.main import UserUpdate

# A valid email should work 
def test_valid_email_passes():
    u = UserUpdate(email="user@example.com")
    assert u.email == "user@example.com"

# An email with whitespace should fail
def test_user_update_whitespace_email():
    with pytest.raises(ValueError):
        UserUpdate(email="   ")

# Checks that an integer email is converted to a string
def test_integer_coerced_to_string_and_passes():
    u = UserUpdate(email=123)
    assert u.email == "123"

# Checks that a long valid email is accepted
def test_long_email_string_passes():
    long_email = "a" * 1000 + "@example.com"
    u = UserUpdate(email=long_email)
    assert u.email == long_email
