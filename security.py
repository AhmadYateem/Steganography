"""
Security Module - Encryption and Decryption

This module provides cryptographic security features for steganography:
- Password-based encryption/decryption using Fernet (AES-128-CBC + HMAC)
- Key derivation from passwords
- Password strength verification
- Random password generation

All functions are re-exported from crypto.py for clean API organization.
"""

# Re-export all encryption/decryption functions from crypto module
from crypto import (
    # Core encryption/decryption
    encrypt_message,
    decrypt_message,
    encrypt_bytes,
    decrypt_bytes,

    # Key derivation
    derive_key_from_password,

    # Password utilities
    hash_password,
    generate_random_password,
    verify_password_strength,

    # Metadata
    get_encryption_info
)

__all__ = [
    'encrypt_message',
    'decrypt_message',
    'encrypt_bytes',
    'decrypt_bytes',
    'derive_key_from_password',
    'hash_password',
    'generate_random_password',
    'verify_password_strength',
    'get_encryption_info'
]
