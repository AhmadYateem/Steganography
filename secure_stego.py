"""
Secure Steganography - Combining Encryption with Zero-Width Character Hiding

This module provides high-level functions that combine encryption and steganography
for maximum security. Messages are encrypted first, then hidden using ZWC steganography.

This implements defense-in-depth security:
1. Encryption provides confidentiality (even if steganography is detected)
2. Steganography provides concealment (hides the existence of the message)
"""

import text_stego
import crypto


def secure_encode(cover_text: str, secret_message: str, password: str,
                  encoding_bits: int = 2, insertion_method: str = 'between_words') -> str:
    """
    SECURE ENCODE PIPELINE: Encrypt message, then hide in cover text.

    This is the high-level function you should use for secure steganography.

    Pipeline steps:
    1. Encrypt message with password (AES-256-CTR)
    2. Convert encrypted data to binary
    3. Encode binary as zero-width characters
    4. Insert ZWC into cover text

    Args:
        cover_text: Normal visible text to hide the message in
        secret_message: Secret message to hide (will be encrypted)
        password: Password for encryption (choose a strong password!)
        encoding_bits: 1 or 2 (2 is recommended for 50% space savings)
        insertion_method: 'append', 'between_words', or 'distributed'

    Returns:
        Stego-text that looks like cover_text but contains encrypted hidden message

    Example:
        >>> cover = "The weather is nice today."
        >>> secret = "Meet at the park at 5pm"
        >>> password = "supersecret123"
        >>>
        >>> stego = secure_encode(cover, secret, password)
        >>> # stego looks like: "The weather is nice today."
        >>> # but contains encrypted hidden message

    Security features:
        - AES-256-CTR encryption
        - PBKDF2 key derivation (100,000 iterations)
        - Random salt and nonce for each encryption
        - Invisible zero-width character encoding
    """
    # Step 1: Encrypt the message
    encrypted_base64 = crypto.encrypt_message(secret_message, password)

    # Step 2: Hide encrypted data using ZWC steganography
    stego_text = text_stego.encode_message(
        cover_text,
        encrypted_base64,
        encoding_bits=encoding_bits,
        insertion_method=insertion_method
    )

    return stego_text


def secure_decode(stego_text: str, password: str, encoding_bits: int = 2) -> str:
    """
    SECURE DECODE PIPELINE: Extract hidden data, then decrypt.

    This reverses the secure_encode process to recover the original message.

    Pipeline steps:
    1. Extract zero-width characters from stego text
    2. Convert ZWC to binary to encrypted data
    3. Decrypt with password
    4. Return original message

    Args:
        stego_text: Text containing hidden encrypted message
        password: Password for decryption (must match encoding password)
        encoding_bits: Must match the encoding_bits used during encoding

    Returns:
        Original decrypted message

    Raises:
        ValueError: If password is incorrect or data is corrupted

    Example:
        >>> message = secure_decode(stego, "supersecret123")
        >>> print(message)  # "Meet at the park at 5pm"

    Note:
        If you get a decryption error, check:
        - Password is correct
        - encoding_bits matches the value used during encoding
        - Stego-text hasn't been modified
    """
    # Step 1: Extract hidden data from ZWC steganography
    encrypted_base64 = text_stego.decode_message(stego_text, encoding_bits=encoding_bits)

    # Step 2: Decrypt the message
    try:
        original_message = crypto.decrypt_message(encrypted_base64, password)
        return original_message
    except Exception as e:
        raise ValueError(f"Failed to decrypt message: {e}\n"
                        "Check that password and encoding_bits are correct.")


def secure_encode_simple(cover_text: str, secret_message: str, password: str) -> str:
    """
    Simplified secure encoding with default parameters.

    Uses recommended defaults:
    - 2-bit encoding (more efficient)
    - between_words insertion (more distributed)

    Args:
        cover_text: Normal visible text
        secret_message: Secret message to hide
        password: Encryption password

    Returns:
        Stego-text with encrypted hidden message
    """
    return secure_encode(cover_text, secret_message, password,
                        encoding_bits=2, insertion_method='between_words')


def secure_decode_simple(stego_text: str, password: str) -> str:
    """
    Simplified secure decoding with default parameters.

    Uses recommended defaults:
    - 2-bit encoding

    Args:
        stego_text: Text with hidden message
        password: Decryption password

    Returns:
        Original decrypted message
    """
    return secure_decode(stego_text, password, encoding_bits=2)


# Additional utility functions

def verify_stego_text(stego_text: str, password: str, encoding_bits: int = 2) -> dict:
    """
    Verify and analyze stego-text without revealing the message.

    Args:
        stego_text: Text to analyze
        password: Password to attempt decryption
        encoding_bits: Encoding bits to use

    Returns:
        Dictionary with verification results
    """
    analysis = text_stego.analyze_text(stego_text)

    result = {
        'has_hidden_data': analysis['has_hidden_data'],
        'visible_text': text_stego.get_visible_text(stego_text),
        'zwc_count': analysis['zwc_chars'],
        'decryption_successful': False,
        'message_length': 0,
        'error': None
    }

    if analysis['has_hidden_data']:
        try:
            message = secure_decode(stego_text, password, encoding_bits)
            result['decryption_successful'] = True
            result['message_length'] = len(message)
        except Exception as e:
            result['error'] = str(e)

    return result


def get_capacity_estimate(cover_text: str, encoding_bits: int = 2) -> dict:
    """
    Estimate how much encrypted data can be hidden in cover text.

    Args:
        cover_text: Cover text to analyze
        encoding_bits: 1 or 2

    Returns:
        Dictionary with capacity information
    """
    # For encrypted data, we need to account for:
    # - Salt: 16 bytes
    # - Nonce: 16 bytes
    # - Ciphertext: same length as message
    # - Base64 encoding: increases size by ~33%

    encryption_overhead = 32  # salt + nonce in bytes
    base64_overhead_factor = 1.33

    # Calculate how many characters of cover text we have
    cover_length = len(cover_text)

    # Each character can potentially hide data
    # But this depends on insertion method
    # For conservative estimate, assume we can use the cover text length

    # Estimate maximum message size
    # Very rough estimate for demonstration
    info = {
        'cover_text_length': cover_length,
        'encoding_bits': encoding_bits,
        'encryption_overhead': f'{encryption_overhead} bytes',
        'note': 'Capacity depends on insertion method and text structure'
    }

    return info


def compare_methods(cover_text: str, secret_message: str, password: str) -> dict:
    """
    Compare different encoding methods for the same message.

    Args:
        cover_text: Cover text
        secret_message: Secret message
        password: Password

    Returns:
        Dictionary comparing different approaches
    """
    results = {}

    # Test different encoding bits
    for bits in [1, 2]:
        # Test different insertion methods
        for method in ['append', 'between_words', 'distributed']:
            key = f'{bits}bit_{method}'
            try:
                stego = secure_encode(cover_text, secret_message, password,
                                     encoding_bits=bits, insertion_method=method)

                analysis = text_stego.analyze_text(stego)

                # Verify decoding works
                decoded = secure_decode(stego, password, encoding_bits=bits)
                decode_success = (decoded == secret_message)

                results[key] = {
                    'encoding_bits': bits,
                    'insertion_method': method,
                    'total_length': len(stego),
                    'zwc_count': analysis['zwc_chars'],
                    'overhead': analysis['zwc_chars'],
                    'decode_success': decode_success
                }
            except Exception as e:
                results[key] = {
                    'encoding_bits': bits,
                    'insertion_method': method,
                    'error': str(e)
                }

    return results


# Quick reference guide (as module docstring addition)
USAGE_GUIDE = """
QUICK REFERENCE: Secure Steganography

=== BASIC USAGE ===

# Encode (hide encrypted message):
from secure_stego import secure_encode, secure_decode

cover = "This is normal text that anyone can see."
secret = "This is the hidden secret message!"
password = "myStrongPassword123"

stego = secure_encode(cover, secret, password)
# stego looks exactly like cover text but contains encrypted secret

# Decode (extract and decrypt message):
message = secure_decode(stego, password)
# message == "This is the hidden secret message!"


=== ADVANCED OPTIONS ===

# 1-bit encoding (uses more ZWC but simpler):
stego = secure_encode(cover, secret, password, encoding_bits=1)

# Different insertion methods:
stego = secure_encode(cover, secret, password, insertion_method='distributed')

# Options: 'append', 'between_words', 'distributed'


=== SECURITY NOTES ===

1. Use strong passwords (at least 12 characters, mixed case, numbers, symbols)
2. Never reuse passwords
3. Keep encoding_bits consistent between encode/decode
4. Encrypted data survives stego detection (encryption still protects message)
5. Both encryption AND steganography must fail for message to be compromised


=== ERROR HANDLING ===

try:
    message = secure_decode(stego, password)
except ValueError as e:
    print(f"Decryption failed: {e}")
    # Wrong password, wrong encoding_bits, or corrupted data
"""


def print_usage_guide():
    """Print the quick reference guide."""
    print(USAGE_GUIDE)
