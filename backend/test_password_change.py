import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.database import get_db, Base
from backend.db.models import User
from backend.core.security import hash_password


DATABASE_URL = "sqlite:///:memory:" #creates a sqlite db in memory instead of file

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db #replaces all instances of the production db with the test one

@pytest.fixture(scope="function")
def setup():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine) #cleans the db after each test so tests are atomic


def test_change_password_success(setup):
    session = TestingSessionLocal()
    user = User(email="Test@email.com",
                first_name = "Test",
                last_name = "User",
                password_hash = hash_password("Test123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    user_id = user.id
    
    # Simulate logging in to get the token
    login_response = client.post("/login", json={
        "email": "Test@email.com",
        "password": "Test123"
    })
    print(login_response.json())
    assert login_response.status_code == 200

    #get credentials needed for password change
    token = login_response.json().get("access_token")

    # Now test the password change
    new_password = "NewPass456"  # The new password for the user
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "Test123",  # The old password
        "new_password": new_password  # The new password
    }, headers={"Authorization": f"Bearer {token}"})
    
    # Assert that the password was updated
    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}

    # close the session
    session.close()

def test_change_password_failure_same(setup):
    session = TestingSessionLocal()
    user = User(email="Test@email.com",
                first_name = "Test",
                last_name = "User",
                password_hash = hash_password("Test123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    user_id = user.id
    
    # Simulate logging in to get the token
    login_response = client.post("/login", json={
        "email": "Test@email.com",
        "password": "Test123"
    })
    print(login_response.json())
    assert login_response.status_code == 200

    #get credentials needed for password change
    token = login_response.json().get("access_token")

    # Now test the password change
    new_password = "Test123"  # The new password for the user
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "Test123",  # The old password
        "new_password": new_password  # The new password
    }, headers={"Authorization": f"Bearer {token}"})
    
    # Assert that the password was updated
    assert response.status_code == 400
    assert response.json() == {"detail": "Old password cannot be the same as new password"}

    # close the session
    session.close()

def test_change_password_failure_incorrect(setup):
    session = TestingSessionLocal()
    user = User(email="Test@email.com",
                first_name = "Test",
                last_name = "User",
                password_hash = hash_password("Test123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    user_id = user.id
    
    # Simulate logging in to get the token
    login_response = client.post("/login", json={
        "email": "Test@email.com",
        "password": "Test123"
    })
    print(login_response.json())
    assert login_response.status_code == 200

    #get credentials needed for password change
    token = login_response.json().get("access_token")

    # Now test the password change
    new_password = "Test456"  # The new password for the user
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "wrongpassword!",  # The old password incorrect
        "new_password": new_password  # The new password
    }, headers={"Authorization": f"Bearer {token}"})
    
    # Assert that the password was updated
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect password"}

    # close the session
    session.close()

def test_change_password_failure_empty_fields(setup):
    session = TestingSessionLocal()
    user = User(email="Test@email.com",
                first_name = "Test",
                last_name = "User",
                password_hash = hash_password("Test123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    user_id = user.id
    
    # Simulate logging in to get the token
    login_response = client.post("/login", json={
        "email": "Test@email.com",
        "password": "Test123"
    })
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    # Empty current_password
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "",
        "new_password": "NewPass456"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (400,422)

    # Empty new_password
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "Test123",
        "new_password": ""
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (400, 422)

    # Both empty
    response = client.put(f"/users/{user_id}/password", json={
        "current_password": "",
        "new_password": ""
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (400,422)
    session.close()