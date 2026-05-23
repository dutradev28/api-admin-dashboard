from infrastructure.security.hashing import hash_password, verify_password

def test_password_hashing():
    pwd = "secret-password"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False
