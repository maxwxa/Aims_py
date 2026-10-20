import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )
    return f"pbkdf2_sha256$600000${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        algorithm, iterations_text, salt_hex, hash_hex = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=len(expected_hash),
    )
    return hmac.compare_digest(password_hash, expected_hash)
