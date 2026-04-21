# This is a script for unit testing for user login using pytest in four methods

import os
from cryptography.fernet import Fernet
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
import pytest
from pydantic import ValidationError
from backend.main import UserLogin


# test 1 valid login credentials
def test_valid_login():
    user = UserLogin(email="user@example.com", password="good_password_123")
    assert user.email == "user@example.com"
    assert user.password == "good_password_123"

# test 2 invalid login value types
def test_invalid_login():
    with pytest.raises(ValueError):
        UserLogin(email=1234, password=5678)  

# test 3 empty username
def test_empty_username():
    with pytest.raises(ValueError):
        UserLogin(email=" ", password="valid_password_987")  # empty email

# test 4 detail on which field failed
def test_login_failure_details():
    with pytest.raises(ValueError):
        UserLogin(email="very_valid@email.com", password="  ")  # empty password")
