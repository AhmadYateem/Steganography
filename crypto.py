"""
Cryptographic functions for secure steganography.

This module provides encryption and decryption functionality using Fernet
(AES-128-CBC with HMAC) to protect secret messages before hiding them with steganography.

Fernet provides:
- AES-128 encryption in CBC mode
- HMAC for authentication
- Automatic key derivation from passwords
- Safe base64 encoding
"""

import base64
import hashlib
import secrets
from cryptography.fernet import Fernet


def derive_key_from_password(password: str) -> bytes:
    """
    Derive a Fernet key from a password.

    Args:
        password: User-provided password string

    Returns:
        32-byte base64-encoded Fernet key

    Note:
        Uses SHA-256 to hash the password into a key.
        For production use, consider PBKDF2 with salt.
    """
    # Hash password to create a consistent 32-byte key
    password_bytes = password.encode('utf-8')
    key_bytes = hashlib.sha256(password_bytes).digest()
    # Fernet requires base64-encoded key
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return fernet_key


def encrypt_message(message: str, password: str) -> str:
    """
    Encrypt a message with a password using Fernet (AES-128-CBC + HMAC).

    Args:
        message: Plain text message to encrypt
        password: Password for encryption

    Returns:
        Base64-encoded encrypted string (Fernet token)

    Example:
        >>> encrypted = encrypt_message("Secret message", "mypassword")
        >>> # Returns base64 string like "gAAAAABhk..."

    Security features:
        - AES-128 encryption in CBC mode
        - HMAC-SHA256 for authentication
        - Timestamp for token expiration (optional)
        - Random IV for each encryption
    """
    # Derive Fernet key from password
    fernet_key = derive_key_from_password(password)

    # Create Fernet cipher
    cipher = Fernet(fernet_key)

    # Encrypt the message
    plaintext = message.encode('utf-8')
    encrypted_token = cipher.encrypt(plaintext)

    # Return as base64 string
    return encrypted_token.decode('ascii')


def decrypt_message(encrypted_token: str, password: str) -> str:
    """
    Decrypt a message encrypted with encrypt_message.

    Args:
        encrypted_token: Base64-encoded Fernet token
        password: Password for decryption (must match encryption password)

    Returns:
        Decrypted plain text message

    Raises:
        ValueError: If password is incorrect or data is corrupted

    Example:
        >>> decrypted = decrypt_message(encrypted, "mypassword")
        >>> print(decrypted)  # "Secret message"
    """
    try:
        # Derive Fernet key from password
        fernet_key = derive_key_from_password(password)

        # Create Fernet cipher
        cipher = Fernet(fernet_key)

        # Decrypt the token
        encrypted_bytes = encrypted_token.encode('ascii')
        decrypted_bytes = cipher.decrypt(encrypted_bytes)

        # Decode UTF-8 to string
        message = decrypted_bytes.decode('utf-8')

        return message

    except Exception as e:
        raise ValueError(f"Decryption failed (wrong password or corrupted data): {e}")


def encrypt_bytes(data: bytes, password: str) -> bytes:
    """
    Encrypt raw bytes with a password using Fernet.

    Args:
        data: Raw bytes to encrypt
        password: Password for encryption

    Returns:
        Encrypted bytes (Fernet token)
    """
    # Derive Fernet key from password
    fernet_key = derive_key_from_password(password)

    # Create Fernet cipher
    cipher = Fernet(fernet_key)

    # Encrypt the data
    encrypted_token = cipher.encrypt(data)

    return encrypted_token


def decrypt_bytes(encrypted_token: bytes, password: str) -> bytes:
    """
    Decrypt bytes encrypted with encrypt_bytes.

    Args:
        encrypted_token: Encrypted Fernet token
        password: Password for decryption

    Returns:
        Decrypted raw bytes

    Raises:
        ValueError: If password is incorrect or data is corrupted
    """
    try:
        # Derive Fernet key from password
        fernet_key = derive_key_from_password(password)

        # Create Fernet cipher
        cipher = Fernet(fernet_key)

        # Decrypt the data
        decrypted_bytes = cipher.decrypt(encrypted_token)

        return decrypted_bytes

    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")


def hash_password(password: str) -> str:
    """
    Create a secure hash of a password (for verification, not encryption).

    Args:
        password: Password to hash

    Returns:
        Hexadecimal string of SHA-256 hash
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_random_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length: Password length (default 16)

    Returns:
        Random password string
    """
    # Use secrets module for cryptographically secure random generation
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


# Utility functions for debugging
def get_encryption_info(encrypted_token: str) -> dict:
    """
    Extract metadata about encrypted data without decrypting.

    Args:
        encrypted_token: Base64-encoded Fernet token

    Returns:
        Dictionary with encryption metadata
    """
    try:
        # Fernet token format: version (1 byte) | timestamp (8 bytes) | IV (16 bytes) | ciphertext (var) | HMAC (32 bytes)
        token_bytes = base64.urlsafe_b64decode(encrypted_token.encode('ascii'))

        return {
            'total_size': len(token_bytes),
            'version': token_bytes[0] if len(token_bytes) > 0 else None,
            'timestamp_size': 8,
            'iv_size': 16,
            'hmac_size': 32,
            'ciphertext_size': len(token_bytes) - 57 if len(token_bytes) > 57 else 0,
            'format': 'Fernet token (1B version + 8B timestamp + 16B IV + ciphertext + 32B HMAC)',
            'encoding': 'base64',
            'algorithm': 'AES-128-CBC with HMAC-SHA256',
            'kdf': 'SHA-256 password hash (for this demo)'
        }
    except Exception as e:
        return {'error': str(e)}


def verify_password_strength(password: str) -> dict:
    """
    Check password strength and provide recommendations.

    Args:
        password: Password to check

    Returns:
        Dictionary with strength assessment
    """
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if length >= 16:
        score += 1
    if has_upper:
        score += 1
    if has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_special:
        score += 1

    if score >= 6:
        strength = "Strong"
    elif score >= 4:
        strength = "Medium"
    else:
        strength = "Weak"

    recommendations = []
    if length < 12:
        recommendations.append("Use at least 12 characters")
    if not has_upper:
        recommendations.append("Add uppercase letters")
    if not has_lower:
        recommendations.append("Add lowercase letters")
    if not has_digit:
        recommendations.append("Add numbers")
    if not has_special:
        recommendations.append("Add special characters")

    return {
        'strength': strength,
        'score': f'{score}/7',
        'length': length,
        'has_uppercase': has_upper,
        'has_lowercase': has_lower,
        'has_digits': has_digit,
        'has_special': has_special,
        'recommendations': recommendations if recommendations else ['Password looks good!']
    }
