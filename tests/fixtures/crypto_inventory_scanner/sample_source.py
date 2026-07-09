import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DIGEST = hashlib.sha256(b"message").hexdigest()
LEGACY_DIGEST = hashlib.md5(b"legacy").hexdigest()

PRIVATE_KEY_MARKER = """-----BEGIN PRIVATE KEY-----
redacted-test-marker
-----END PRIVATE KEY-----"""

def build_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def encrypt(nonce, key, message):
    return AESGCM(key).encrypt(nonce, message, None)
