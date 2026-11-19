from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

password_hasher = PasswordHasher()

pw = "abc123"


def hash_password(password: str) -> str:
    """Erzeugt einen sicheren Argon2id-Hash für die Datenbank."""
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Prüft ein eingegebenes Passwort gegen den gespeicherten Hash."""
    try:
        return password_hasher.verify(stored_hash, password)
    except VerifyMismatchError, InvalidHashError:
        return False


if __name__ == "__main__":
    print(hash_password(pw))
    print(verify_password(pw, hash_password(pw)))