from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hasher = PasswordHasher()

def hash_password(password: str) -> str:
    # Return the Argon2 hash.
    password_hash = hasher.hash(password)
    return password_hash

def verify_password(password: str, stored_hash: str) -> bool:
    # Verify against the stored hash.
    # Return False when VerifyMismatchError occurs.
    try:
        return hasher.verify(stored_hash, password)
    except VerifyMismatchError:
        return False
        