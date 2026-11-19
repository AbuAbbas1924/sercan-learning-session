import os
import time
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

JWT_KEY = os.environ.get("JWT_KEY", "dev-only-secret-change-me")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")

pw_hasher = PasswordHasher()


def verify_pw(plain: str, hashed: str) -> bool:
    try:
        output = pw_hasher.verify(hashed, plain)
        print("verify_pw", output)
        return output
    except VerifyMismatchError, InvalidHashError:
        print("VERIFIED: ", False)
        return False


def create_access_token(user: str, expires: int = 5):
    payload = {
        "sub": user,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires),
        # "expires": expires !there is no expire time
    }
    print("payload", payload)
    encoded = jwt.encode(payload, JWT_KEY, algorithm=ALGORITHM)
    print("encoded", encoded)
    return encoded


def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        decoded = payload["sub"]
        print("decoded", decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        print("expired")
        return "there is no logged user"


# def verify_access_token()

if __name__ == "__main__":
    hashed = pw_hasher.hash("1234")
    print("HASHED", hashed)
    verify_pw("1234", hashed)
    token = create_access_token("Sercan", 3)
    print("before expiring: ", verify_token(token))
    time.sleep(8)
    print("after expiring: ", verify_token(token))