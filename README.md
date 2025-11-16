# Zero-Width Character (ZWC) Text Steganography

A Python implementation of text steganography using invisible Unicode zero-width characters to hide secret messages within normal visible text.

## Overview

This implementation uses zero-width Unicode characters to encode binary data invisibly within regular text. The hidden message is completely invisible to readers, making it an effective steganographic technique.

## Core Functions

### 1. Text to Binary Conversion

**`text_to_binary(text: str) -> str`**

Converts text into a binary string representation.

```python
import text_stego

binary = text_stego.text_to_binary("Hi")
# Returns: "0100100001101001"
```

**Input:** Secret message as normal text
**Output:** String of 0s and 1s (binary representation)

### 2. Binary to Zero-Width Character Mapping

**`binary_to_zwc(binary: str, encoding_bits: int = 1) -> str`**

Maps binary strings to invisible Unicode characters.

#### 1-bit Encoding (Default)
Uses 2 different zero-width characters:
- `0` → U+200C (Zero Width Non-Joiner)
- `1` → U+200D (Zero Width Joiner)

#### 2-bit Encoding (More Efficient)
Uses 4 different zero-width characters:
- `00` → U+200B (Zero Width Space)
- `01` → U+200C (Zero Width Non-Joiner)
- `10` → U+200D (Zero Width Joiner)
- `11` → U+FEFF (Zero Width No-Break Space)

**Benefit:** 2-bit encoding reduces the number of ZWC characters by 50%

```python
# 1-bit encoding
zwc = text_stego.binary_to_zwc("01101000", encoding_bits=1)
# Returns: 8 invisible characters

# 2-bit encoding (more efficient)
zwc = text_stego.binary_to_zwc("01101000", encoding_bits=2)
# Returns: 4 invisible characters (50% reduction)
```

### 3. Hiding Messages in Cover Text

**`encode_message(cover_text: str, secret_message: str, encoding_bits: int = 1, insertion_method: str = 'append') -> str`**

Hides invisible zero-width characters inside normal text.

**Inputs:**
- `cover_text`: Normal visible text to hide the message in
- `secret_message`: Secret message to hide
- `encoding_bits`: Number of bits per ZWC (1 or 2)
- `insertion_method`: How to insert ZWC characters

**Insertion Methods:**

1. **`'append'`** - Add all ZWC at the end (simplest)
2. **`'between_words'`** - Distribute ZWC between words (more subtle)
3. **`'distributed'`** - Spread evenly throughout text (most distributed)

**Example:**

```python
cover = "The quick brown fox jumps over the lazy dog."
secret = "Secret"

# Hide the secret message
stego_text = text_stego.encode_message(cover, secret, encoding_bits=1)

# The stego_text still looks like: "The quick brown fox jumps over the lazy dog."
# But it contains invisible characters hiding "Secret"
```

## Complete Usage Example

```python
import text_stego

# Step 1: Prepare your cover text and secret message
cover_text = "Hello, world! This is a normal message."
secret_message = "Hidden data"

# Step 2: Encode the secret message (hide it)
stego_text = text_stego.encode_message(
    cover_text,
    secret_message,
    encoding_bits=2,  # Use 2-bit encoding for efficiency
    insertion_method='between_words'
)

# Step 3: The stego text looks normal but contains hidden data
print(f"Visible text: {text_stego.get_visible_text(stego_text)}")
# Output: "Hello, world! This is a normal message."

# Step 4: Later, decode the hidden message
decoded = text_stego.decode_message(stego_text, encoding_bits=2)
print(f"Decoded secret: {decoded}")
# Output: "Hidden data"
```

## Additional Functions

### Decoding

**`decode_message(stego_text: str, encoding_bits: int = 1) -> str`**

Extract the hidden message from stego-text.

```python
message = text_stego.decode_message(stego_text, encoding_bits=1)
```

### Analysis

**`analyze_text(text: str) -> dict`**

Analyze text to detect and report ZWC characters.

```python
analysis = text_stego.analyze_text(stego_text)
print(analysis)
# {
#   'total_chars': 92,
#   'visible_chars': 44,
#   'zwc_chars': 48,
#   'has_hidden_data': True,
#   'zwc_breakdown': {'U+200C': 30, 'U+200D': 18}
# }
```

### Get Visible Text

**`get_visible_text(stego_text: str) -> str`**

Remove all ZWC characters to see only visible text.

```python
visible = text_stego.get_visible_text(stego_text)
```

## Running the Demo

Run the demonstration script to see all features in action:

```bash
python demo.py
```

The demo showcases:
1. Text to binary conversion
2. Binary to ZWC mapping (1-bit and 2-bit)
3. Encoding messages with different insertion methods
4. Text analysis and ZWC detection
5. Comparison of 1-bit vs 2-bit encoding efficiency

## Technical Details

### Unicode Characters Used

| Character | Code Point | Name | Usage |
|-----------|------------|------|-------|
| U+200B | `\u200B` | Zero Width Space | 2-bit: `00` |
| U+200C | `\u200C` | Zero Width Non-Joiner | 1-bit: `0`, 2-bit: `01` |
| U+200D | `\u200D` | Zero Width Joiner | 1-bit: `1`, 2-bit: `10` |
| U+FEFF | `\uFEFF` | Zero Width No-Break Space | 2-bit: `11` |

### Encoding Process

1. **Text → Binary:** Convert secret message to binary using UTF-8 encoding (8 bits per character)
2. **Binary → ZWC:** Map binary sequences to invisible Unicode characters
3. **Insertion:** Insert ZWC characters into cover text using chosen method

### Decoding Process

1. **Extract ZWC:** Filter out only zero-width characters from stego-text
2. **ZWC → Binary:** Convert ZWC back to binary string
3. **Binary → Text:** Convert binary to text using UTF-8 decoding

## Performance Comparison

For a 6-character secret message "Secret" (48 bits):

| Encoding | ZWC Count | Overhead | Efficiency |
|----------|-----------|----------|------------|
| 1-bit | 48 chars | High | Simple |
| 2-bit | 24 chars | Low | **50% reduction** |

## File Structure

```
Steganography/
├── text_stego.py    # Core ZWC steganography module
├── demo.py          # Demonstration script
└── README.md        # This file
```

## Features Implemented

✅ Text to binary conversion
✅ Binary to ZWC mapping (1-bit and 2-bit)
✅ Message encoding with multiple insertion methods
✅ Message decoding
✅ Text analysis for ZWC detection
✅ Visible text extraction
✅ Comprehensive demonstration

## Next Steps (Not Yet Implemented)

The following features are part of the complete project but not implemented yet:

- AES-256 encryption wrapper for security
- Cryptographic random position selection
- Image steganography (LSB, DCT, DWT methods)
- Web interface
- Steganalysis tools
- Robustness testing

## License

Educational project for cryptography capstone course.
