from infrastructure.security.hashing import hash_password, verify_password
from infrastructure.security.tokens import create_access_token, decode_access_token

def test_password_hashing():
    pwd = "secret-password"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_jwt_create_and_decode():
    data = {"sub": "user@example.com", "role": "admin"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]

def test_jwt_invalid_token():
    assert decode_access_token("invalid-token") is None
