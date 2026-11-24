from argon2 import PasswordHasher

hasher = PasswordHasher()

password = "my-test-password"
password_hash = hasher.hash(password)

print(password_hash)
print(hasher.verify(password_hash, "my-test-password"))
# print(hasher.verify(password_hash, "wrong-password"))