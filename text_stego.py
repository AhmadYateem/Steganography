"""
Zero-Width Character (ZWC) Text Steganography

This module implements text steganography using invisible Unicode zero-width characters.
Secret messages are encoded as binary and then mapped to zero-width characters that are
hidden within normal visible text.
"""


# Zero-width Unicode characters used for steganography
# Basic 1-bit encoding
ZWC_0 = '\u200C'  # Zero Width Non-Joiner (ZWNJ)
ZWC_1 = '\u200D'  # Zero Width Joiner (ZWJ)

# Extended 2-bit encoding (4 characters for 00, 01, 10, 11)
ZWC_00 = '\u200B'  # Zero Width Space
ZWC_01 = '\u200C'  # Zero Width Non-Joiner
ZWC_10 = '\u200D'  # Zero Width Joiner
ZWC_11 = '\uFEFF'  # Zero Width No-Break Space


def text_to_binary(text: str) -> str:
    """
    Convert text to binary representation.

    Args:
        text: Secret message as normal text

    Returns:
        String of 0s and 1s (binary representation)

    Example:
        >>> text_to_binary("Hi")
        '0100100001101001'
    """
    # Convert each character to its UTF-8 byte representation, then to binary
    binary_result = []

    for char in text:
        # Get the Unicode code point of the character
        code_point = ord(char)
        # Convert to binary (without '0b' prefix) and pad to 8 bits
        binary = bin(code_point)[2:].zfill(8)
        binary_result.append(binary)

    return ''.join(binary_result)


def binary_to_text(binary: str) -> str:
    """
    Convert binary string back to text.

    Args:
        binary: String of 0s and 1s

    Returns:
        Decoded text string

    Example:
        >>> binary_to_text("0100100001101001")
        'Hi'
    """
    # Split binary string into 8-bit chunks
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:  # Only process complete bytes
            # Convert binary to integer, then to character
            char = chr(int(byte, 2))
            chars.append(char)

    return ''.join(chars)


def binary_to_zwc(binary: str, encoding_bits: int = 1) -> str:
    """
    Map binary string to invisible zero-width characters.

    Args:
        binary: String of 0s and 1s
        encoding_bits: Number of bits to encode at once (1 or 2)
                      1 bit: uses 2 ZWC characters (0, 1)
                      2 bits: uses 4 ZWC characters (00, 01, 10, 11)

    Returns:
        String of invisible zero-width characters

    Example:
        >>> zwc = binary_to_zwc("01")
        >>> # Returns invisible characters representing the binary
    """
    if encoding_bits == 1:
        # Simple 1-bit encoding: 0 → ZWC_0, 1 → ZWC_1
        zwc_chars = []
        for bit in binary:
            if bit == '0':
                zwc_chars.append(ZWC_0)
            elif bit == '1':
                zwc_chars.append(ZWC_1)
            else:
                raise ValueError(f"Invalid binary character: {bit}")
        return ''.join(zwc_chars)

    elif encoding_bits == 2:
        # 2-bit encoding: 00, 01, 10, 11 → four different ZWC characters
        # Pad binary string to even length if needed
        if len(binary) % 2 != 0:
            binary += '0'

        zwc_chars = []
        for i in range(0, len(binary), 2):
            two_bits = binary[i:i+2]
            if two_bits == '00':
                zwc_chars.append(ZWC_00)
            elif two_bits == '01':
                zwc_chars.append(ZWC_01)
            elif two_bits == '10':
                zwc_chars.append(ZWC_10)
            elif two_bits == '11':
                zwc_chars.append(ZWC_11)

        return ''.join(zwc_chars)

    else:
        raise ValueError("encoding_bits must be 1 or 2")


def zwc_to_binary(zwc_text: str, encoding_bits: int = 1) -> str:
    """
    Convert zero-width characters back to binary string.

    Args:
        zwc_text: String containing zero-width characters
        encoding_bits: Number of bits per ZWC (1 or 2)

    Returns:
        Binary string (0s and 1s)
    """
    binary_result = []

    if encoding_bits == 1:
        for char in zwc_text:
            if char == ZWC_0:
                binary_result.append('0')
            elif char == ZWC_1:
                binary_result.append('1')
            # Ignore other characters (visible text)

    elif encoding_bits == 2:
        for char in zwc_text:
            if char == ZWC_00:
                binary_result.append('00')
            elif char == ZWC_01:
                binary_result.append('01')
            elif char == ZWC_10:
                binary_result.append('10')
            elif char == ZWC_11:
                binary_result.append('11')
            # Ignore other characters

    return ''.join(binary_result)


def encode_message(cover_text: str, secret_message: str, encoding_bits: int = 1,
                   insertion_method: str = 'append') -> str:
    """
    Hide invisible zero-width characters inside normal text.

    Args:
        cover_text: Normal visible text to hide the message in
        secret_message: Secret message to hide
        encoding_bits: Number of bits to encode per ZWC (1 or 2)
        insertion_method: How to insert ZWC characters
                         'append': Add all ZWC at the end
                         'between_words': Distribute ZWC between words
                         'distributed': Spread evenly throughout text

    Returns:
        Stego-text containing both visible cover text and invisible secret message

    Example:
        >>> stego = encode_message("Hello world", "Secret", encoding_bits=1)
        >>> # Returns text that looks like "Hello world" but contains hidden message
    """
    # Step 1: Convert secret message to binary
    binary = text_to_binary(secret_message)

    # Step 2: Convert binary to invisible ZWC characters
    zwc_string = binary_to_zwc(binary, encoding_bits)

    # Step 3: Insert ZWC characters into cover text
    if insertion_method == 'append':
        # Simple approach: append all ZWC at the end
        stego_text = cover_text + zwc_string

    elif insertion_method == 'between_words':
        # Insert ZWC between words (spaces)
        words = cover_text.split(' ')
        zwc_per_space = len(zwc_string) // max(len(words) - 1, 1)

        if len(words) <= 1:
            # No spaces to insert between, fall back to append
            stego_text = cover_text + zwc_string
        else:
            result = [words[0]]
            zwc_index = 0

            for i in range(1, len(words)):
                # Add some ZWC characters before the next word
                zwc_chunk_size = min(zwc_per_space, len(zwc_string) - zwc_index)
                if zwc_chunk_size > 0:
                    result.append(zwc_string[zwc_index:zwc_index + zwc_chunk_size])
                    zwc_index += zwc_chunk_size

                result.append(' ')
                result.append(words[i])

            # Append any remaining ZWC characters
            if zwc_index < len(zwc_string):
                result.append(zwc_string[zwc_index:])

            stego_text = ''.join(result)

    elif insertion_method == 'distributed':
        # Spread ZWC evenly throughout the text
        if len(cover_text) == 0:
            stego_text = zwc_string
        else:
            interval = max(len(cover_text) // len(zwc_string), 1) if zwc_string else 0
            result = []
            zwc_index = 0

            for i, char in enumerate(cover_text):
                result.append(char)
                # Insert ZWC at regular intervals
                if interval > 0 and (i + 1) % interval == 0 and zwc_index < len(zwc_string):
                    result.append(zwc_string[zwc_index])
                    zwc_index += 1

            # Append any remaining ZWC
            if zwc_index < len(zwc_string):
                result.append(zwc_string[zwc_index:])

            stego_text = ''.join(result)

    else:
        raise ValueError(f"Unknown insertion_method: {insertion_method}")

    return stego_text


def decode_message(stego_text: str, encoding_bits: int = 1) -> str:
    """
    Extract hidden message from stego-text.

    Args:
        stego_text: Text containing hidden zero-width characters
        encoding_bits: Number of bits per ZWC (1 or 2)

    Returns:
        Decoded secret message

    Example:
        >>> message = decode_message(stego_text, encoding_bits=1)
        >>> print(message)  # "Secret"
    """
    # Step 1: Extract ZWC characters and convert to binary
    binary = zwc_to_binary(stego_text, encoding_bits)

    # Step 2: Convert binary back to text
    try:
        message = binary_to_text(binary)
        return message
    except Exception as e:
        raise ValueError(f"Failed to decode message: {e}")


def get_visible_text(stego_text: str) -> str:
    """
    Extract only the visible characters from stego-text.

    Args:
        stego_text: Text potentially containing ZWC characters

    Returns:
        Only the visible text, with ZWC removed
    """
    # Define all ZWC characters we use
    zwc_chars = {ZWC_0, ZWC_1, ZWC_00, ZWC_01, ZWC_10, ZWC_11}

    # Filter out ZWC characters
    visible = ''.join(char for char in stego_text if char not in zwc_chars)
    return visible


# Utility functions for debugging and analysis
def analyze_text(text: str) -> dict:
    """
    Analyze text to detect and report ZWC characters.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with analysis results
    """
    zwc_chars = {ZWC_0, ZWC_1, ZWC_00, ZWC_01, ZWC_10, ZWC_11}

    zwc_count = sum(1 for char in text if char in zwc_chars)
    visible_count = len(text) - zwc_count

    zwc_breakdown = {}
    for char in zwc_chars:
        count = text.count(char)
        if count > 0:
            zwc_breakdown[f'U+{ord(char):04X}'] = count

    return {
        'total_chars': len(text),
        'visible_chars': visible_count,
        'zwc_chars': zwc_count,
        'has_hidden_data': zwc_count > 0,
        'zwc_breakdown': zwc_breakdown
    }
