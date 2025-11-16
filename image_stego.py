"""
LSB (Least Significant Bit) Image Steganography

This module implements steganography for images using the LSB technique.
Secret messages are hidden by modifying the least significant bits of pixel values.

Organization:
- Section 1: Constants and Configuration
- Section 2: Bit Manipulation Helpers
- Section 3: Image Loading/Saving (B1)
- Section 4: LSB Encoding (B1)
- Section 5: LSB Decoding (B1)
- Section 6: Multi-bit Capacity (B2)
- Section 7: Utility Functions
"""

from PIL import Image
import numpy as np
from typing import Tuple, Optional


# ============================================================================
# SECTION 1: CONSTANTS AND CONFIGURATION
# ============================================================================

# Header size: number of bytes used to store the message length
# We use 4 bytes = 32 bits, allowing messages up to 4GB (more than enough)
HEADER_SIZE_BYTES = 4

# Supported image formats
SUPPORTED_FORMATS = ['PNG', 'BMP', 'TIFF']

# Color channels
CHANNEL_RED = 0
CHANNEL_GREEN = 1
CHANNEL_BLUE = 2

# Default encoding parameters
DEFAULT_BITS_PER_PIXEL = 1  # How many LSBs to modify per pixel
DEFAULT_CHANNEL = CHANNEL_BLUE  # Which color channel to use


# ============================================================================
# SECTION 2: BIT MANIPULATION HELPERS
# ============================================================================

def message_to_bits(message: str) -> str:
    """
    Convert a text message to a binary string.

    Args:
        message: Text message to convert

    Returns:
        String of '0' and '1' characters representing the message

    Example:
        >>> message_to_bits("Hi")
        '0100100001101001'
    """
    bits = []
    for char in message:
        # Get ASCII/Unicode value
        char_value = ord(char)
        # Convert to 8-bit binary (without '0b' prefix)
        char_bits = format(char_value, '08b')
        bits.append(char_bits)
    return ''.join(bits)


def bits_to_message(bits: str) -> str:
    """
    Convert a binary string back to a text message.

    Args:
        bits: String of '0' and '1' characters

    Returns:
        Decoded text message

    Example:
        >>> bits_to_message('0100100001101001')
        'Hi'
    """
    chars = []
    # Process 8 bits at a time
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:  # Only process complete bytes
            char_value = int(byte, 2)
            chars.append(chr(char_value))
    return ''.join(chars)


def int_to_bits(value: int, num_bits: int = 32) -> str:
    """
    Convert an integer to a binary string of fixed length.

    Args:
        value: Integer to convert
        num_bits: Number of bits in output (default 32)

    Returns:
        Binary string of specified length

    Example:
        >>> int_to_bits(5, 8)
        '00000101'
    """
    return format(value, f'0{num_bits}b')


def bits_to_int(bits: str) -> int:
    """
    Convert a binary string to an integer.

    Args:
        bits: String of '0' and '1' characters

    Returns:
        Integer value

    Example:
        >>> bits_to_int('00000101')
        5
    """
    return int(bits, 2)


def modify_lsb(pixel_value: int, bit: str, num_lsb: int = 1) -> int:
    """
    Modify the least significant bit(s) of a pixel value.

    This is the core of LSB steganography!

    Args:
        pixel_value: Original pixel value (0-255)
        bit: Bit value to encode ('0' or '1')
        num_lsb: Number of LSBs to modify (1, 2, or 3)

    Returns:
        Modified pixel value

    Example:
        >>> modify_lsb(254, '1', 1)  # 11111110 -> 11111111
        255
        >>> modify_lsb(255, '0', 1)  # 11111111 -> 11111110
        254
    """
    if num_lsb == 1:
        # Clear the last bit, then set it to the new bit value
        # Example: 11111110 & 11111110 = 11111110, then | 1 = 11111111
        pixel_value = (pixel_value & 0xFE) | int(bit)

    elif num_lsb == 2:
        # Clear the last 2 bits, then set them
        # Mask: 11111100 (0xFC)
        pixel_value = (pixel_value & 0xFC) | int(bit, 2)

    elif num_lsb == 3:
        # Clear the last 3 bits, then set them
        # Mask: 11111000 (0xF8)
        pixel_value = (pixel_value & 0xF8) | int(bit, 2)

    return pixel_value


def extract_lsb(pixel_value: int, num_lsb: int = 1) -> str:
    """
    Extract the least significant bit(s) from a pixel value.

    Args:
        pixel_value: Pixel value (0-255)
        num_lsb: Number of LSBs to extract (1, 2, or 3)

    Returns:
        Binary string of extracted bits

    Example:
        >>> extract_lsb(255, 1)  # 11111111
        '1'
        >>> extract_lsb(254, 1)  # 11111110
        '0'
        >>> extract_lsb(255, 2)  # 11111111
        '11'
    """
    if num_lsb == 1:
        # Get the last bit: value & 00000001
        return str(pixel_value & 0x01)

    elif num_lsb == 2:
        # Get the last 2 bits: value & 00000011
        bits = pixel_value & 0x03
        return format(bits, '02b')

    elif num_lsb == 3:
        # Get the last 3 bits: value & 00000111
        bits = pixel_value & 0x07
        return format(bits, '03b')

    return '0'


# ============================================================================
# SECTION 3: IMAGE LOADING AND SAVING (B1)
# ============================================================================

def load_image(image_path: str) -> Tuple[np.ndarray, str]:
    """
    Load an image from disk and convert to numpy array.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (pixel_array, image_format)
        - pixel_array: 3D numpy array [height, width, channels]
        - image_format: Original format (PNG, BMP, etc.)

    Raises:
        ValueError: If image format is not supported

    Example:
        >>> pixels, fmt = load_image("secret.png")
        >>> print(pixels.shape)  # (height, width, 3)
    """
    # Open image with Pillow
    img = Image.open(image_path)

    # Check format
    img_format = img.format
    if img_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {img_format}. "
                        f"Supported: {SUPPORTED_FORMATS}")

    # Convert to RGB if needed (handles RGBA, grayscale, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Convert to numpy array [height, width, 3]
    # Each pixel has 3 values: [Red, Green, Blue], each 0-255
    pixel_array = np.array(img, dtype=np.uint8)

    return pixel_array, img_format


def save_image(pixel_array: np.ndarray, output_path: str,
               image_format: str = 'PNG') -> None:
    """
    Save a numpy pixel array as an image file.

    Args:
        pixel_array: 3D numpy array [height, width, channels]
        output_path: Where to save the image
        image_format: Format to save as (PNG, BMP, etc.)

    Example:
        >>> save_image(modified_pixels, "stego.png", "PNG")
    """
    # Create PIL Image from numpy array
    img = Image.fromarray(pixel_array.astype(np.uint8), 'RGB')

    # Save to disk
    img.save(output_path, format=image_format)


def get_image_capacity(image_path: str, bits_per_pixel: int = 1) -> dict:
    """
    Calculate how many bytes can be hidden in an image.

    Args:
        image_path: Path to the image
        bits_per_pixel: How many LSBs to use (1, 2, or 3)

    Returns:
        Dictionary with capacity information

    Example:
        >>> capacity = get_image_capacity("image.png", bits_per_pixel=1)
        >>> print(capacity['max_bytes'])
    """
    pixels, _ = load_image(image_path)
    height, width, channels = pixels.shape

    total_pixels = height * width

    # Each pixel can hide 'bits_per_pixel' bits
    total_bits_available = total_pixels * bits_per_pixel

    # Subtract header size
    header_bits = HEADER_SIZE_BYTES * 8
    usable_bits = total_bits_available - header_bits

    max_bytes = usable_bits // 8

    return {
        'image_dimensions': f'{width}x{height}',
        'total_pixels': total_pixels,
        'bits_per_pixel': bits_per_pixel,
        'total_bits_available': total_bits_available,
        'header_bits': header_bits,
        'usable_bits': usable_bits,
        'max_bytes': max_bytes,
        'max_characters': max_bytes,  # Assuming 1 byte per character
    }


# ============================================================================
# SECTION 4: LSB ENCODING (B1)
# ============================================================================

def encode_lsb(image_path: str, message: str, output_path: str,
               bits_per_pixel: int = 1, channel: int = CHANNEL_BLUE) -> dict:
    """
    Hide a message in an image using LSB steganography.

    This is the main encoding function!

    Pipeline:
    1. Load image
    2. Convert message to bits
    3. Create header with message length
    4. Modify pixel LSBs to encode header + message
    5. Save stego image

    Args:
        image_path: Path to cover image
        message: Secret message to hide
        output_path: Where to save stego image
        bits_per_pixel: How many LSBs to modify (1, 2, or 3)
        channel: Which color channel (0=R, 1=G, 2=B)

    Returns:
        Dictionary with encoding statistics

    Raises:
        ValueError: If message is too large for the image

    Example:
        >>> result = encode_lsb("cover.png", "Secret message", "stego.png")
        >>> print(result['success'])
        True
    """
    # Step 1: Load the image
    pixels, img_format = load_image(image_path)
    height, width, channels = pixels.shape

    # Step 2: Convert message to bits
    message_bits = message_to_bits(message)
    message_length = len(message_bits)

    # Step 3: Create header (stores message length)
    # Header is the message length as a 32-bit integer
    header_bits = int_to_bits(message_length, num_bits=32)

    # Combine header + message
    all_bits = header_bits + message_bits
    total_bits = len(all_bits)

    # Step 4: Check capacity
    total_pixels = height * width
    max_bits = total_pixels * bits_per_pixel

    if total_bits > max_bits:
        raise ValueError(
            f"Message too large! Need {total_bits} bits, "
            f"but image can only hold {max_bits} bits.\n"
            f"Try: (1) smaller message, (2) larger image, "
            f"or (3) more bits_per_pixel"
        )

    # Step 5: Encode bits into pixels
    # We'll modify pixels in row-major order: (0,0), (0,1), (0,2), ...
    bit_index = 0

    for row in range(height):
        for col in range(width):
            if bit_index >= total_bits:
                # All bits encoded!
                break

            # Get the bit(s) to encode
            if bits_per_pixel == 1:
                bit_to_encode = all_bits[bit_index]
                bit_index += 1
            elif bits_per_pixel == 2:
                bit_to_encode = all_bits[bit_index:bit_index+2]
                bit_index += 2
                # Pad if necessary
                if len(bit_to_encode) < 2:
                    bit_to_encode = bit_to_encode.ljust(2, '0')
            elif bits_per_pixel == 3:
                bit_to_encode = all_bits[bit_index:bit_index+3]
                bit_index += 3
                # Pad if necessary
                if len(bit_to_encode) < 3:
                    bit_to_encode = bit_to_encode.ljust(3, '0')
            else:
                raise ValueError("bits_per_pixel must be 1, 2, or 3")

            # Modify the LSB of the selected channel
            original_value = pixels[row, col, channel]
            modified_value = modify_lsb(original_value, bit_to_encode, bits_per_pixel)
            pixels[row, col, channel] = modified_value

        if bit_index >= total_bits:
            break

    # Step 6: Save the stego image
    save_image(pixels, output_path, img_format)

    # Return statistics
    return {
        'success': True,
        'message_length': len(message),
        'message_bits': message_length,
        'header_bits': 32,
        'total_bits_encoded': total_bits,
        'bits_per_pixel': bits_per_pixel,
        'channel_used': ['Red', 'Green', 'Blue'][channel],
        'image_dimensions': f'{width}x{height}',
        'pixels_modified': bit_index // bits_per_pixel,
        'capacity_used_percent': (total_bits / max_bits) * 100,
        'output_path': output_path
    }


# ============================================================================
# SECTION 5: LSB DECODING (B1)
# ============================================================================

def decode_lsb(stego_image_path: str, bits_per_pixel: int = 1,
               channel: int = CHANNEL_BLUE) -> str:
    """
    Extract a hidden message from a stego image.

    This is the main decoding function!

    Pipeline:
    1. Load stego image
    2. Extract header (first 32 bits) to get message length
    3. Extract message bits (based on length from header)
    4. Convert bits back to text

    Args:
        stego_image_path: Path to stego image
        bits_per_pixel: How many LSBs were used (1, 2, or 3)
        channel: Which color channel was used (0=R, 1=G, 2=B)

    Returns:
        Decoded secret message

    Example:
        >>> message = decode_lsb("stego.png", bits_per_pixel=1)
        >>> print(message)
        'Secret message'
    """
    # Step 1: Load the stego image
    pixels, _ = load_image(stego_image_path)
    height, width, channels = pixels.shape

    # Step 2: Extract ALL bits we need in one pass
    # First extract header to know message length, then extract that many bits

    extracted_bits = []
    pixel_index = 0
    total_pixels = height * width

    # First, extract header (32 bits)
    header_bits_needed = 32
    bits_collected = 0

    while bits_collected < header_bits_needed and pixel_index < total_pixels:
        row = pixel_index // width
        col = pixel_index % width

        pixel_value = pixels[row, col, channel]
        lsb = extract_lsb(pixel_value, bits_per_pixel)
        extracted_bits.append(lsb)
        bits_collected += len(lsb)
        pixel_index += 1

    # Decode header to get message length
    header_bits_str = ''.join(extracted_bits)[:32]
    message_length_bits = bits_to_int(header_bits_str)

    # Now extract message bits
    total_bits_needed = 32 + message_length_bits

    while bits_collected < total_bits_needed and pixel_index < total_pixels:
        row = pixel_index // width
        col = pixel_index % width

        pixel_value = pixels[row, col, channel]
        lsb = extract_lsb(pixel_value, bits_per_pixel)
        extracted_bits.append(lsb)
        bits_collected += len(lsb)
        pixel_index += 1

    # Step 4: Convert bits to message
    all_bits_str = ''.join(extracted_bits)
    message_bits_str = all_bits_str[32:32 + message_length_bits]

    decoded_message = bits_to_message(message_bits_str)

    return decoded_message


# ============================================================================
# SECTION 6: MULTI-BIT CAPACITY (B2)
# ============================================================================

def encode_lsb_variable(image_path: str, message: str, output_path: str,
                        bits_per_pixel: int = 1) -> dict:
    """
    Encode with user-controlled capacity (1, 2, or 3 bits per pixel).

    This is a convenience wrapper for encode_lsb with validation.

    Args:
        image_path: Path to cover image
        message: Secret message
        output_path: Where to save stego image
        bits_per_pixel: 1 (least impact), 2 (medium), or 3 (most capacity)

    Returns:
        Encoding statistics

    Example:
        >>> # High capacity mode (more visible changes)
        >>> result = encode_lsb_variable("cover.png", "Long message...",
        ...                              "stego.png", bits_per_pixel=3)
    """
    if bits_per_pixel not in [1, 2, 3]:
        raise ValueError("bits_per_pixel must be 1, 2, or 3")

    return encode_lsb(image_path, message, output_path,
                     bits_per_pixel=bits_per_pixel)


def decode_lsb_variable(stego_image_path: str, bits_per_pixel: int = 1) -> str:
    """
    Decode with user-controlled capacity.

    Args:
        stego_image_path: Path to stego image
        bits_per_pixel: Must match the value used during encoding!

    Returns:
        Decoded message
    """
    if bits_per_pixel not in [1, 2, 3]:
        raise ValueError("bits_per_pixel must be 1, 2, or 3")

    return decode_lsb(stego_image_path, bits_per_pixel=bits_per_pixel)


# ============================================================================
# SECTION 7: UTILITY FUNCTIONS
# ============================================================================

def compare_images(original_path: str, stego_path: str) -> dict:
    """
    Compare original and stego images to measure visual difference.

    Args:
        original_path: Path to original image
        stego_path: Path to stego image

    Returns:
        Dictionary with comparison metrics
    """
    orig_pixels, _ = load_image(original_path)
    stego_pixels, _ = load_image(stego_path)

    # Calculate differences
    diff = np.abs(orig_pixels.astype(int) - stego_pixels.astype(int))

    # Statistics
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    pixels_changed = np.count_nonzero(diff)
    total_pixels = orig_pixels.shape[0] * orig_pixels.shape[1] * orig_pixels.shape[2]

    return {
        'max_difference': int(max_diff),
        'mean_difference': float(mean_diff),
        'pixels_changed': int(pixels_changed),
        'total_pixels': int(total_pixels),
        'change_percentage': (pixels_changed / total_pixels) * 100,
        'imperceptible': max_diff <= 3  # LSB changes should be ≤1 per bit
    }


def create_test_image(width: int = 512, height: int = 512,
                     output_path: str = 'test_image.png') -> None:
    """
    Create a simple test image for demonstrations.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        output_path: Where to save the test image
    """
    # Create a gradient image for testing
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    for row in range(height):
        for col in range(width):
            # Red gradient
            img_array[row, col, 0] = int((col / width) * 255)
            # Green gradient
            img_array[row, col, 1] = int((row / height) * 255)
            # Blue constant
            img_array[row, col, 2] = 128

    save_image(img_array, output_path, 'PNG')


# ============================================================================
# CONVENIENCE FUNCTIONS (Simple API)
# ============================================================================

def hide_message(image_path: str, message: str, output_path: str = 'stego.png',
                 quality: str = 'standard') -> dict:
    """
    Simple API: Hide a message in an image.

    Args:
        image_path: Cover image path
        message: Secret message
        output_path: Output stego image path
        quality: 'high' (1 bit), 'standard' (2 bits), or 'fast' (3 bits)

    Returns:
        Encoding statistics
    """
    quality_map = {
        'high': 1,      # Least visible, least capacity
        'standard': 2,  # Balanced
        'fast': 3       # Most capacity, most visible
    }

    bits = quality_map.get(quality, 2)
    return encode_lsb(image_path, message, output_path, bits_per_pixel=bits)


def extract_message(stego_path: str, quality: str = 'standard') -> str:
    """
    Simple API: Extract a message from a stego image.

    Args:
        stego_path: Stego image path
        quality: Must match the quality used during encoding

    Returns:
        Decoded message
    """
    quality_map = {
        'high': 1,
        'standard': 2,
        'fast': 3
    }

    bits = quality_map.get(quality, 2)
    return decode_lsb(stego_path, bits_per_pixel=bits)
