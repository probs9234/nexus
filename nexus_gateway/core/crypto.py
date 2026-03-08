from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def generate_key() -> bytes:
    """Generates a secure 256-bit AES key."""
    return AESGCM.generate_key(bit_length=256)

def encrypt_data(key: bytes, data: bytes) -> bytes:
    """
    Encrypts data using AES-256-GCM.
    Prepends the 12-byte nonce to the resulting ciphertext.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(key: bytes, encrypted_data: bytes) -> bytes:
    """
    Decrypts data using AES-256-GCM.
    Extracts the 12-byte nonce from the beginning of the data before decrypting.
    """
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)
