import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, StaticPool
from presentation.api.main import app
from presentation.api.dependencies import get_session
from infrastructure.database.models import UserModel, AccountantModel
from infrastructure.security.hashing import hash_password

# Setup in-memory database for testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_signup_success(client: TestClient, session: Session):
    payload = {
        "name": "New Accountant",
        "cnpj": "12345678901234",
        "email": "new@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    assert response.json()["message"] == "Account created successfully"
    assert "accountant_id" in response.json()

def test_signup_duplicate_email(client: TestClient, session: Session):
    # Setup
    user = UserModel(
        email="existing@example.com",
        password_hash="hash",
        role="accountant"
    )
    session.add(user)
    session.commit()

    payload = {
        "name": "Another",
        "cnpj": "987654321",
        "email": "existing@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client: TestClient, session: Session):
    # Setup
    user = UserModel(
        email="user@example.com",
        password_hash=hash_password("correct_password"),
        role="accountant"
    )
    session.add(user)
    session.commit()

    payload = {
        "email": "user@example.com",
        "password": "correct_password"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure(client: TestClient, session: Session):
    payload = {
        "email": "wrong@example.com",
        "password": "password"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_forgot_password_success(client: TestClient, session: Session):
    # Setup
    user = UserModel(
        email="recover@example.com",
        password_hash="hash",
        role="accountant"
    )
    session.add(user)
    session.commit()

    payload = {"email": "recover@example.com"}
    response = client.post("/api/v1/auth/forgot-password", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["message"] == "Recovery token generated"

def test_reset_password_success(client: TestClient, session: Session):
    # Setup
    user = UserModel(
        email="reset@example.com",
        password_hash=hash_password("old_password"),
        role="accountant"
    )
    session.add(user)
    session.commit()

    # Get token
    payload_forgot = {"email": "reset@example.com"}
    response_forgot = client.post("/api/v1/auth/forgot-password", json=payload_forgot)
    token = response_forgot.json()["token"]

    # Reset
    payload_reset = {
        "token": token,
        "new_password": "new_password123"
    }
    response_reset = client.post("/api/v1/auth/reset-password", json=payload_reset)
    assert response_reset.status_code == 200
    assert response_reset.json()["message"] == "Password reset successfully"

    # Verify login with new password
    payload_login = {
        "email": "reset@example.com",
        "password": "new_password123"
    }
    response_login = client.post("/api/v1/auth/login", json=payload_login)
    assert response_login.status_code == 200
