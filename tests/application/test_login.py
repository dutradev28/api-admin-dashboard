import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from application.queries.login import LoginQuery, LoginHandler
from infrastructure.database.models import UserModel
from infrastructure.security.hashing import hash_password
from infrastructure.security.tokens import decode_access_token
from domain.entities.user import UserRole

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_login_success(session: Session):
    # Given
    email = "test@example.com"
    password = "password123"
    hashed_pw = hash_password(password)
    user = UserModel(
        email=email,
        password_hash=hashed_pw,
        role=UserRole.ACCOUNTANT.value,
        accountant_id="acc-123"
    )
    session.add(user)
    session.commit()

    query = LoginQuery(email=email, password=password)
    handler = LoginHandler(session)

    # When
    token = handler.handle(query)

    # Then
    assert token is not None
    payload = decode_access_token(token)
    assert payload["sub"] == email
    assert payload["role"] == UserRole.ACCOUNTANT.value
    assert payload["accountant_id"] == "acc-123"

def test_login_invalid_password(session: Session):
    # Given
    email = "test@example.com"
    password = "password123"
    hashed_pw = hash_password(password)
    user = UserModel(
        email=email,
        password_hash=hashed_pw,
        role=UserRole.ACCOUNTANT.value
    )
    session.add(user)
    session.commit()

    query = LoginQuery(email=email, password="wrongpassword")
    handler = LoginHandler(session)

    # When / Then
    with pytest.raises(ValueError, match="Invalid email or password"):
        handler.handle(query)

def test_login_user_not_found(session: Session):
    # Given
    query = LoginQuery(email="nonexistent@example.com", password="password123")
    handler = LoginHandler(session)

    # When / Then
    with pytest.raises(ValueError, match="Invalid email or password"):
        handler.handle(query)
