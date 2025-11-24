# Image Steganography Guide
## LSB (Least Significant Bit) Technique

**Complete guide to hiding messages in images using LSB steganography**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [How LSB Works (Simple Explanation)](#how-lsb-works-simple-explanation)
3. [Module Organization](#module-organization)
4. [B1: Basic LSB Implementation](#b1-basic-lsb-implementation)
5. [B2: Multi-Bit Capacity](#b2-multi-bit-capacity)
6. [Complete Examples](#complete-examples)
7. [Understanding the Header System](#understanding-the-header-system)
8. [Capacity Planning](#capacity-planning)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Simplest Usage (3 lines)

```python
from image_stego import hide_message, extract_message

# Hide a secret in an image
hide_message('photo.png', 'My secret message!', 'stego.png')

# Extract the secret
message = extract_message('stego.png')
print(message)  # "My secret message!"
```

---

## How LSB Works (Simple Explanation)

### What is LSB?

LSB = **Least Significant Bit** (the last bit of a number)

Images are made of pixels. Each pixel has 3 color values (Red, Green, Blue), each 0-255.

### Example:

A pixel's Blue value might be **`254`** in binary: **`11111110`**

```
Position:  7 6 5 4 3 2 1 0  ← bit positions
Binary:    1 1 1 1 1 1 1 0
           ↑             ↑
           MSB          LSB  ← Least Significant Bit
```

### The Magic Trick:

**Changing the LSB from 0 to 1 changes the value from 254 to 255**

```
Before: 11111110 = 254  (original)
After:  11111111 = 255  (with secret bit '1' hidden)
```

**The difference of 1 is INVISIBLE to the human eye!**

### Hiding a Message:

1. Convert message to binary: "Hi" → `01001000 01101001`
2. Change LSBs of pixels to match each bit
3. Save the image (looks identical to original)

### Extracting:

1. Read LSBs from each pixel
2. Collect bits: `01001000 01101001`
3. Convert back to text: "Hi"

**That's LSB steganography! 🎉**

---

## Module Organization

### File Structure

```
image_stego.py          ← Main module (all functions)
├── Section 1: Constants
├── Section 2: Bit Manipulation Helpers
├── Section 3: Image Loading/Saving (B1)
├── Section 4: LSB Encoding (B1)
├── Section 5: LSB Decoding (B1)
├── Section 6: Multi-bit Capacity (B2)
└── Section 7: Utility Functions
```

### Key Functions by Section:

**Section 3: Image I/O**
- `load_image()` - Load PNG/BMP/TIFF
- `save_image()` - Save modified image
- `get_image_capacity()` - Check how much you can hide

**Section 4: Encoding**
- `encode_lsb()` - Hide message in image
- `modify_lsb()` - Change pixel LSBs

**Section 5: Decoding**
- `decode_lsb()` - Extract message from image
- `extract_lsb()` - Read pixel LSBs

**Section 6: Multi-bit**
- `encode_lsb_variable()` - User-controlled capacity (1-3 bits)
- `decode_lsb_variable()` - Decode multi-bit

**Section 7: Utils**
- `hide_message()` - Simple API for encoding
- `extract_message()` - Simple API for decoding
- `compare_images()` - Measure visual difference
- `create_test_image()` - Generate test images

---

## B1: Basic LSB Implementation

### Requirement B1 Breakdown:

**✅ Load and save images**
```python
pixels, format = load_image("photo.png")
# pixels = 3D array [height, width, 3]
# format = 'PNG' or 'BMP' or 'TIFF'

save_image(pixels, "output.png", "PNG")
```

**✅ Hide bits in LSBs (encode)**
```python
result = encode_lsb(
    image_path="cover.png",
    message="Secret!",
    output_path="stego.png",
    bits_per_pixel=1  # Modify 1 LSB per pixel
)
```

**✅ Read bits back (decode)**
```python
message = decode_lsb(
    stego_image_path="stego.png",
    bits_per_pixel=1  # Must match encoding!
)
```

**✅ Message length header**
- First 32 bits store message length
- Decoder reads header to know when to stop
- No need to specify message length when decoding!

### Step-by-Step Encoding Process:

```python
# What happens when you call encode_lsb():

# Step 1: Load image
pixels = load_image("cover.png")  # [height, width, 3]

# Step 2: Convert message to bits
message = "Hi"
# 'H' = 72 = 01001000
# 'i' = 105 = 01101001
# Total = "0100100001101001" (16 bits)

# Step 3: Create header (message length)
header = int_to_bits(16, 32)  # 32-bit integer
# header = "00000000000000000000000000010000"

# Step 4: Combine header + message
all_bits = header + message_bits
# Total = 32 + 16 = 48 bits to encode

# Step 5: Modify pixels
for each bit in all_bits:
    pixel_value = pixels[row, col, BLUE]  # Use blue channel
    modified = modify_lsb(pixel_value, bit)
    pixels[row, col, BLUE] = modified

# Step 6: Save
save_image(pixels, "stego.png")
```

### Step-by-Step Decoding Process:

```python
# What happens when you call decode_lsb():

# Step 1: Load stego image
pixels = load_image("stego.png")

# Step 2: Extract header (first 32 bits)
for first 32 pixels:
    bit = extract_lsb(pixels[row, col, BLUE])
    header_bits += bit

message_length = bits_to_int(header_bits)  # = 16

# Step 3: Extract message bits
for next 16 pixels:
    bit = extract_lsb(pixels[row, col, BLUE])
    message_bits += bit

# Step 4: Convert to text
message = bits_to_message(message_bits)  # = "Hi"
```

---

## B2: Multi-Bit Capacity

### What is Multi-Bit Capacity?

Instead of changing **1 bit** per pixel, change **2 or 3 bits**.

### Comparison:

| Bits/Pixel | Capacity | Visual Impact | Max Change |
|------------|----------|---------------|------------|
| 1 bit | Lowest | Invisible | ±1 |
| 2 bits | Medium | Nearly invisible | ±3 |
| 3 bits | Highest | Slightly visible | ±7 |

### Example: 2-bit encoding

```
Original pixel: 11111110 = 254
Want to hide: '11' (2 bits)

Clear last 2 bits:  11111100 (& 0xFC)
Set to '11':        11111111 (| 3)
Result: 255 (difference of 1)
```

### Usage:

```python
# === 1-bit (safest) ===
encode_lsb(img, msg, out, bits_per_pixel=1)

# === 2-bits (balanced) ===
encode_lsb(img, msg, out, bits_per_pixel=2)

# === 3-bits (maximum capacity) ===
encode_lsb(img, msg, out, bits_per_pixel=3)
```

### When to use each:

**1-bit: Maximum stealth**
- Use when: Image will be analyzed
- Pros: Completely invisible
- Cons: Lowest capacity

**2-bits: Recommended default**
- Use when: Normal use cases
- Pros: Good balance
- Cons: None really

**3-bits: Maximum capacity**
- Use when: Need to hide large messages
- Pros: Highest capacity
- Cons: May be slightly visible on close inspection

---

## Complete Examples

### Example 1: Basic Hiding (B1)

```python
import image_stego

# Hide a message
result = image_stego.encode_lsb(
    image_path="vacation_photo.png",
    message="Secret meeting at 5pm",
    output_path="vacation_photo_stego.png",
    bits_per_pixel=1
)

print(f"Encoded {result['message_length']} characters")
print(f"Used {result['capacity_used_percent']:.2f}% of capacity")

# Extract the message
decoded = image_stego.decode_lsb(
    stego_image_path="vacation_photo_stego.png",
    bits_per_pixel=1
)

print(f"Secret message: {decoded}")
```

### Example 2: Multi-bit Capacity (B2)

```python
import image_stego

cover = "large_photo.png"
long_message = "This is a very long secret message..." * 50

# Check capacity for different bit settings
for bits in [1, 2, 3]:
    capacity = image_stego.get_image_capacity(cover, bits_per_pixel=bits)
    print(f"{bits} bit(s): Can hide {capacity['max_bytes']:,} bytes")

# Encode with 2-bit (balanced)
result = image_stego.encode_lsb_variable(
    image_path=cover,
    message=long_message,
    output_path="stego_2bit.png",
    bits_per_pixel=2  # More capacity than 1-bit
)

# Decode (must use same bits_per_pixel!)
decoded = image_stego.decode_lsb_variable(
    "stego_2bit.png",
    bits_per_pixel=2
)

assert decoded == long_message
```

### Example 3: Simple API (Easiest)

```python
from image_stego import hide_message, extract_message

# Hide (uses smart defaults)
hide_message(
    image_path="photo.png",
    message="My secret",
    output_path="stego.png",
    quality='standard'  # or 'high' or 'fast'
)

# Extract
message = extract_message("stego.png", quality='standard')
print(message)
```

### Example 4: Check Image Before Encoding

```python
import image_stego

# Check capacity first
capacity = image_stego.get_image_capacity(
    "small_image.png",
    bits_per_pixel=1
)

print(f"This image can hide {capacity['max_characters']} characters")

# Try to encode
message = "X" * 10000  # Too large?

if len(message) > capacity['max_characters']:
    print(f"Message too large! Use {2} bits or larger image")
else:
    image_stego.encode_lsb("small_image.png", message, "stego.png")
```

### Example 5: Compare Visual Impact

```python
import image_stego

cover = "original.png"
message = "Test message"

# Encode with different settings
for bits in [1, 2, 3]:
    stego = f"stego_{bits}bit.png"
    image_stego.encode_lsb(cover, message, stego, bits_per_pixel=bits)

    # Compare
    diff = image_stego.compare_images(cover, stego)
    print(f"{bits} bit(s):")
    print(f"  Max difference: {diff['max_difference']}")
    print(f"  Imperceptible: {diff['imperceptible']}")
```

---

## Understanding the Header System

### Why Do We Need a Header?

**Problem:** How does the decoder know when to stop reading?

Without header:
- Decoder doesn't know message length
- Reads too many bits → garbage at the end
- Or reads too few bits → incomplete message

**Solution:** Store message length in first 32 bits

### Header Format:

```
[32-bit header][message bits...]
      ↓
Message length

Example:
Message: "Hi" (16 bits)
Header: 00000000000000000000000000010000 (32 bits = number 16)
Total in image: 00000000000000000000000000010000 0100100001101001
                └────── header ──────┘ └─ message ─┘
```

### Encoding with Header:

```python
# Automatic! Just call encode_lsb()
result = encode_lsb(img, "Hi", "stego.png")

# Behind the scenes:
# 1. Converts "Hi" to bits (16 bits)
# 2. Creates header: int_to_bits(16, 32)
# 3. Combines: header + message
# 4. Encodes all 48 bits
```

### Decoding with Header:

```python
# Automatic! Just call decode_lsb()
message = decode_lsb("stego.png")

# Behind the scenes:
# 1. Extracts first 32 bits
# 2. Converts to integer: length = 16
# 3. Extracts next 16 bits
# 4. Converts to text: "Hi"
```

### Header Size:

32 bits = 4 bytes = can store numbers up to 4,294,967,295

This means maximum message size is ~4GB (way more than images can hold!)

---

## Capacity Planning

### How Much Can You Hide?

**Formula:**
```
Max bits = (width × height × bits_per_pixel) - 32
Max bytes = Max bits / 8
Max characters ≈ Max bytes (for ASCII)
```

### Examples:

**Small image (256×256):**
- 1 bit/pixel: ~8,188 characters
- 2 bits/pixel: ~16,380 characters
- 3 bits/pixel: ~24,572 characters

**Medium image (512×512):**
- 1 bit/pixel: ~32,764 characters
- 2 bits/pixel: ~65,532 characters
- 3 bits/pixel: ~98,300 characters

**Large image (1920×1080 Full HD):**
- 1 bit/pixel: ~259,196 characters
- 2 bits/pixel: ~518,396 characters
- 3 bits/pixel: ~777,596 characters

### Quick Check:

```python
capacity = image_stego.get_image_capacity("photo.png", bits_per_pixel=2)
print(f"Can hide: {capacity['max_characters']:,} characters")
```

### What if Message is Too Large?

**Option 1: Use more bits per pixel**
```python
# Instead of 1 bit
encode_lsb(img, msg, out, bits_per_pixel=2)  # 2× capacity!
```

**Option 2: Use larger image**
```python
# Use 1920×1080 instead of 800×600
```

**Option 3: Compress message**
```python
import zlib
compressed = zlib.compress(message.encode())
# Then hide compressed bytes
```

**Option 4: Combine with encryption**
```python
# Encryption is already implemented in secure_stego.py!
from secure_stego import secure_encode
# This encrypts first, then hides
```

---

## Troubleshooting

### Problem: "Message too large" error

**Cause:** Message doesn't fit in image

**Solution:**
```python
# Check capacity first
cap = image_stego.get_image_capacity(img, bits_per_pixel=1)
if len(message) > cap['max_characters']:
    # Use more bits or larger image
    image_stego.encode_lsb(img, msg, out, bits_per_pixel=2)
```

---

### Problem: Decoded message is corrupted

**Cause:** Wrong `bits_per_pixel` during decoding

**Solution:**
```python
# bits_per_pixel MUST match between encode and decode

# Encode with 2 bits
encode_lsb(img, msg, "stego.png", bits_per_pixel=2)

# Decode with 2 bits (not 1!)
decode_lsb("stego.png", bits_per_pixel=2)
```

---

### Problem: Decoded message has garbage at end

**Cause:** This shouldn't happen (header prevents it)

**Solution:** If you see this, there's a bug. The header system should prevent reading beyond the message.

---

### Problem: Image looks different after encoding

**Cause:** Using too many bits per pixel

**Analysis:**
```python
# Check visual impact
diff = image_stego.compare_images("orig.png", "stego.png")
print(f"Max difference: {diff['max_difference']}")

# If max_difference > 7:
#   Something is wrong!
# If max_difference = 1:
#   Perfect (1-bit encoding)
# If max_difference = 3:
#   Good (2-bit encoding)
# If max_difference = 7:
#   Acceptable (3-bit encoding)
```

**Solution:** Use fewer bits per pixel (1 instead of 3)

---

### Problem: Can't load image

**Cause:** Unsupported format

**Supported formats:**
- PNG ✅ (Recommended - lossless)
- BMP ✅ (Lossless but large files)
- TIFF ✅ (Lossless)
- JPEG ❌ (Lossy compression destroys hidden data!)

**Solution:** Convert to PNG first:
```python
from PIL import Image
img = Image.open("photo.jpg")
img.save("photo.png", "PNG")
# Now use photo.png
```

---

### Problem: Want to hide in JPEG

**Why it doesn't work:**
JPEG uses lossy compression that changes pixel values, destroying hidden LSB data.

**Solutions:**
1. Use PNG instead (lossless)
2. Or use DCT-based steganography (not implemented yet, part of future work)

---

## Best Practices

### 1. Always Use PNG Format

```python
# ✓ Good
hide_message("photo.png", msg, "stego.png")

# ✗ Bad (JPEG is lossy!)
hide_message("photo.jpg", msg, "stego.jpg")
```

### 2. Check Capacity Before Encoding

```python
# ✓ Good
cap = get_image_capacity("img.png", bits_per_pixel=1)
if len(message) <= cap['max_characters']:
    encode_lsb("img.png", message, "stego.png")

# ✗ Bad (may fail)
encode_lsb("img.png", huge_message, "stego.png")
```

### 3. Use 2-bit Encoding as Default

```python
# ✓ Balanced (recommended)
encode_lsb(img, msg, out, bits_per_pixel=2)

# Also OK for maximum stealth
encode_lsb(img, msg, out, bits_per_pixel=1)

# Use sparingly (more visible)
encode_lsb(img, msg, out, bits_per_pixel=3)
```

### 4. Always Match bits_per_pixel

```python
# ✓ Good
encode_lsb(img, msg, "stego.png", bits_per_pixel=2)
decode_lsb("stego.png", bits_per_pixel=2)  # Same!

# ✗ Bad (will produce garbage)
encode_lsb(img, msg, "stego.png", bits_per_pixel=2)
decode_lsb("stego.png", bits_per_pixel=1)  # Different!
```

### 5. Verify Round-Trip

```python
# ✓ Good practice
original_msg = "Secret!"
encode_lsb("img.png", original_msg, "stego.png")
decoded_msg = decode_lsb("stego.png")
assert decoded_msg == original_msg  # Verify!
```

---

## Quick Reference

### Encode Message:
```python
from image_stego import hide_message
hide_message('photo.png', 'Secret!', 'stego.png')
```

### Decode Message:
```python
from image_stego import extract_message
msg = extract_message('stego.png')
```

### Check Capacity:
```python
from image_stego import get_image_capacity
cap = get_image_capacity('photo.png', bits_per_pixel=1)
print(f"Can hide {cap['max_characters']} characters")
```

### Compare Images:
```python
from image_stego import compare_images
diff = compare_images('original.png', 'stego.png')
print(f"Max change: {diff['max_difference']}")
```

---

## Module Summary

| Component | Purpose | Key Functions |
|-----------|---------|---------------|
| **B1: Basic LSB** | Core encoding/decoding | `encode_lsb()`, `decode_lsb()` |
| **B2: Multi-bit** | Variable capacity | `encode_lsb_variable()` (1-3 bits) |
| **Header System** | Message length | Automatic (built-in) |
| **Image I/O** | Load/save images | `load_image()`, `save_image()` |
| **Simple API** | Easy usage | `hide_message()`, `extract_message()` |

---

**Run the demo to see everything in action:**
```bash
python demo_image.py
```

**Check the main README.md for the complete project documentation.**
