import secrets


def generate_secret_key(length: int = 32) -> str:
    """Generates a secure secret key."""
    return secrets.token_hex(length)


secret_key = generate_secret_key()
print(f"Generated Secret Key: {secret_key}")
