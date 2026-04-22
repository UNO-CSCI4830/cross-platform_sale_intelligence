# This is a script for unit testing for user login using pytest in four methods

import os
from cryptography.fernet import Fernet
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
import pytest
from pydantic import ValidationError
from backend.main import UserLogin


# test 1 valid login credentials
def test_valid_login():
    email = "user1@example.com"
    password = "good_password_123"
    user = UserLogin(email=email, password=password)
    assert user.email == email
    assert user.password == password

# test 2 invalid login value types - strings are accepted but integers are not
def test_invalid_login():
    with pytest.raises(ValueError):
        email = 1234  # invalid email type
        password = 5678  # invalid password type
        UserLogin(email=email, password=password)  

# test 3 empty username - user name should not be empty
def test_empty_username():
    with pytest.raises(ValueError):
        email = " "  # empty email
        password = "valid_password_987"
        UserLogin(email=email, password=password)  # empty email

# test 4 empty password - password should not be empty
def test_login_failure_details():
    with pytest.raises(ValueError):
        email = "very_valid2@email.com"
        password = "  "  # empty password
        UserLogin(email=email, password=password)
