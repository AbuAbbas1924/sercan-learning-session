import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hasher = PasswordHasher()

async def hash_password(password: str) -> str:
    # Return the Argon2 hash.
    return await asyncio.to_thread(hasher.hash, password)

async def verify_password(password: str, stored_hash: str) -> bool:
    # Verify against the stored hash.
    # Return False when VerifyMismatchError occurs.
    try:
        return await asyncio.to_thread(hasher.verify, stored_hash, password)
    except VerifyMismatchError:
        return False
