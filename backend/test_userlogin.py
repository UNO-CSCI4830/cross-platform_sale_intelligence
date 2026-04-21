# This is a script for unit testing for user login using pytest in four methods

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import UserLogin
from streamlit import login

# test 1 valid login credentials
def test_valid_login():
    username = "user@example.com"
    password = "good_password_123"
    assert UserLogin(username, password) == "Login successful" 

# test 2 invalid login value types
def test_invalid_login():
    username = 1234
    password = 5678
    assert UserLogin(username, password) == "Login failed - Invalid input types"  

# test 3 empty username
def test_empty_username():
    username = " "
    password = "valid_password_987"
    assert UserLogin(username, password) == "Login failed - Empty username" 

# test 4 detail on which field failed
def test_login_failure_details():
    username = "valid_user"
    password = "   " # empty password
    result = UserLogin(username, password)
    assert result == "Login failed: Incorrect password - Password cannot be empty"
