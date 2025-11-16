# Complete Steganography Suite
## Text & Image Steganography with Encryption

A comprehensive implementation of steganography supporting **both text and images** with optional encryption for maximum security.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Module Documentation](#module-documentation)
  - [TEXT: A1 & A2 - ZWC Steganography (text_stego.py)](#text-a1--a2---zwc-steganography-text_stegopy)
  - [TEXT: A3 - Encryption (crypto.py)](#text-a3---encryption-cryptopy)
  - [TEXT: Secure Pipeline (secure_stego.py)](#text-secure-pipeline-secure_stegopy)
  - [IMAGE: B1 & B2 - LSB Steganography (image_stego.py)](#image-b1--b2---lsb-steganography-image_stegopy)
- [Complete Examples](#complete-examples)
- [Security Features](#security-features)
- [Running Demos](#running-demos)
- [Technical Details](#technical-details)

---

## Overview

This project implements **seven main components**:

### Text Steganography (A1, A2, A3)
1. **Zero-Width Character (ZWC) Steganography** - Hide messages in invisible Unicode characters
2. **AES Encryption** - Encrypt messages before hiding for maximum security
3. **Secure Pipeline** - High-level API combining both for defense-in-depth

### Image Steganography (B1, B2, C)
4. **LSB (Least Significant Bit) Encoding** - Hide messages by modifying image pixels
5. **Multi-bit Capacity** - User-controlled capacity (1, 2, or 3 bits per pixel)
6. **Quality Metrics** - MSE, PSNR, SSIM for measuring imperceptibility

### Web API (D1, D2)
7. **Flask REST API** - HTTP endpoints for encoding, decoding, and analyzing steganography

### Why This Approach?

**Defense-in-Depth Security:**
- **Encryption** protects confidentiality (even if steganography is detected, message remains encrypted)
- **Steganography** provides concealment (attacker doesn't know a message exists)
- **Both must fail** for message to be compromised

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Using the Web Interface (Recommended - Easiest!)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (choose one):
python start.py          # Cross-platform launcher (recommended)
# OR
python app.py           # Direct launch
# OR
./start.sh             # Linux/Mac only
# OR
start.bat              # Windows (or double-click it)
```

Open your browser and navigate to: **http://localhost:5000**

You'll see a stunning, Apple-level professional interface with:
- ✨ Beautiful dark mode design with smooth animations
- 🎨 Drag-and-drop file upload
- 📊 Real-time quality metrics visualization
- 🖼️ Side-by-side image comparison
- 🔒 One-click encoding/decoding
- 💾 Direct download of stego images

See **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** for complete frontend documentation.

### Using the Web API (For Developers - D1, D2)

```bash
# Start the Flask server
python app.py

# Server runs on http://localhost:5000
```

**Test with curl:**
```bash
# Health check
curl http://localhost:5000/ping

# Hide message in text
curl -X POST http://localhost:5000/api/encode \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "zwc",
    "cover_text": "Hello world",
    "secret_message": "Secret!",
    "password": "mypass"
  }'
```

See **[API_GUIDE.md](API_GUIDE.md)** for complete API documentation with Python examples.

### Using Python Modules Directly

#### Basic Usage (Secure Mode - Recommended)

```python
from secure_stego import secure_encode, secure_decode

# Alice: Hide encrypted message in normal text
cover_text = "The weather is nice today. Hope you're doing well!"
secret_message = "Meet at the park at 5pm"
password = "strongPassword123"

# Encode: encrypt + hide
stego_text = secure_encode(cover_text, secret_message, password)
# stego_text looks like: "The weather is nice today. Hope you're doing well!"
# But contains invisible encrypted message!

# Bob: Extract and decrypt
decoded_message = secure_decode(stego_text, password)
# decoded_message == "Meet at the park at 5pm"
```

### Without Encryption (Not Recommended for Sensitive Data)

```python
import text_stego

# Encode
stego = text_stego.encode_message(cover_text, secret_message)

# Decode
message = text_stego.decode_message(stego)
```

---

## Project Structure

```
Steganography/
├── Core Modules:
│   ├── text_stego.py       # A1 & A2: ZWC encoder/decoder
│   ├── crypto.py           # A3: Encryption module
│   ├── secure_stego.py     # Combined secure steganography
│   ├── image_stego.py      # B1 & B2: LSB image steganography
│   ├── metrics.py          # C: Image quality metrics (MSE, PSNR, SSIM)
│   └── security.py         # Security module wrapper
│
├── Web API & Frontend (D1, D2, E):
│   ├── app.py              # Flask REST API server
│   ├── test_api.py         # API validation tests
│   └── static/
│       └── index.html      # Beautiful frontend interface
│
├── Demos:
│   ├── demo.py             # Demo: Basic ZWC steganography
│   ├── demo_secure.py      # Demo: Encrypted steganography
│   └── demo_image.py       # Demo: LSB image steganography
│
├── Documentation:
│   ├── README.md           # This file - complete overview
│   ├── USAGE_GUIDE.md      # Text steganography guide
│   ├── IMAGE_GUIDE.md      # Image steganography guide
│   ├── METRICS_GUIDE.md    # Quality metrics guide
│   ├── API_GUIDE.md        # Web API documentation
│   └── FRONTEND_GUIDE.md   # Frontend interface guide
│
└── requirements.txt        # Python dependencies
```

---

## Module Documentation

### A1 & A2: Text Steganography (text_stego.py)

Implements zero-width character encoding and decoding.

#### A1: Encoder Functions

##### 1. `text_to_binary(text: str) -> str`

Convert text to binary representation.

```python
binary = text_stego.text_to_binary("Hi")
# Returns: "0100100001101001" (16 bits for 2 characters)
```

**Input:** String message
**Output:** Binary string (0s and 1s)

---

##### 2. `binary_to_zwc(binary: str, encoding_bits: int = 1) -> str`

Map binary to invisible zero-width characters.

**1-bit Encoding (Default):**
- Uses 2 ZWC characters
- `0` → U+200C (Zero Width Non-Joiner)
- `1` → U+200D (Zero Width Joiner)

**2-bit Encoding (Recommended - 50% more efficient):**
- Uses 4 ZWC characters
- `00` → U+200B (Zero Width Space)
- `01` → U+200C (Zero Width Non-Joiner)
- `10` → U+200D (Zero Width Joiner)
- `11` → U+FEFF (Zero Width No-Break Space)

```python
# 1-bit: 8 characters for 8 bits
zwc_1 = text_stego.binary_to_zwc("01101000", encoding_bits=1)

# 2-bit: 4 characters for 8 bits (50% reduction!)
zwc_2 = text_stego.binary_to_zwc("01101000", encoding_bits=2)
```

---

##### 3. `encode_message(cover_text, secret_message, encoding_bits=1, insertion_method='append')`

Hide invisible characters inside cover text.

**Parameters:**
- `cover_text`: Normal visible text
- `secret_message`: Secret message to hide
- `encoding_bits`: 1 or 2 (2 recommended)
- `insertion_method`:
  - `'append'` - Add all ZWC at end (simplest)
  - `'between_words'` - Distribute between words (more subtle)
  - `'distributed'` - Spread evenly (most distributed)

```python
stego = text_stego.encode_message(
    "Hello world",
    "Secret",
    encoding_bits=2,
    insertion_method='between_words'
)
# stego looks like: "Hello world" (but contains hidden "Secret")
```

---

#### A2: Decoder Functions

##### 4. `zwc_to_binary(zwc_text: str, encoding_bits: int = 1) -> str`

Convert zero-width characters back to binary.

```python
binary = text_stego.zwc_to_binary(zwc_string, encoding_bits=2)
```

---

##### 5. `decode_message(stego_text: str, encoding_bits: int = 1) -> str`

Extract hidden message from stego-text.

**Pipeline:**
1. Extract ZWC characters
2. Convert ZWC → binary
3. Convert binary → text

```python
message = text_stego.decode_message(stego_text, encoding_bits=2)
```

---

#### Utility Functions

##### `analyze_text(text: str) -> dict`

Analyze text for hidden ZWC characters.

```python
analysis = text_stego.analyze_text(stego_text)
# {
#   'total_chars': 92,
#   'visible_chars': 44,
#   'zwc_chars': 48,
#   'has_hidden_data': True,
#   'zwc_breakdown': {'U+200C': 30, 'U+200D': 18}
# }
```

##### `get_visible_text(stego_text: str) -> str`

Remove all ZWC to see only visible text.

```python
visible = text_stego.get_visible_text(stego_text)
```

---

### A3: Encryption (crypto.py)

Provides encryption/decryption using Fernet (AES-128-CBC with HMAC).

#### Core Functions

##### `encrypt_message(message: str, password: str) -> str`

Encrypt a message with a password.

```python
encrypted = crypto.encrypt_message("Secret message", "myPassword123")
# Returns: "gAAAAABhk2L..." (base64-encoded Fernet token)
```

**Security Features:**
- AES-128 encryption in CBC mode
- HMAC-SHA256 for authentication
- Random IV for each encryption
- Timestamp included in token

---

##### `decrypt_message(encrypted_token: str, password: str) -> str`

Decrypt a message.

```python
message = crypto.decrypt_message(encrypted, "myPassword123")
# Returns: "Secret message"
```

**Raises:** `ValueError` if password is wrong or data is corrupted

---

#### Utility Functions

##### `verify_password_strength(password: str) -> dict`

Check password strength.

```python
strength = crypto.verify_password_strength("weak")
# {
#   'strength': 'Weak',
#   'score': '2/7',
#   'recommendations': ['Use at least 12 characters', ...]
# }
```

##### `generate_random_password(length: int = 16) -> str`

Generate cryptographically secure password.

```python
password = crypto.generate_random_password(20)
# Returns: "xK9mP2vL#qR4$nW7..."
```

---

### Secure Steganography (secure_stego.py)

**High-level API combining encryption + steganography.**

#### Main Functions

##### `secure_encode(cover_text, secret_message, password, encoding_bits=2, insertion_method='between_words')`

**Complete encoding pipeline:**
1. Encrypt message with password (AES)
2. Convert encrypted data → binary
3. Encode binary as ZWC
4. Insert ZWC into cover text

```python
stego = secure_stego.secure_encode(
    cover_text="The weather is nice today.",
    secret_message="Meet at 5pm",
    password="mySecurePassword",
    encoding_bits=2,  # Recommended
    insertion_method='between_words'
)
```

---

##### `secure_decode(stego_text, password, encoding_bits=2)`

**Complete decoding pipeline:**
1. Extract ZWC from stego text
2. Convert ZWC → binary → encrypted data
3. Decrypt with password
4. Return original message

```python
message = secure_stego.secure_decode(
    stego_text=stego,
    password="mySecurePassword",
    encoding_bits=2
)
```

**Raises:** `ValueError` if password is wrong or encoding_bits doesn't match

---

#### Simplified API

##### `secure_encode_simple(cover_text, secret_message, password)`

Uses recommended defaults (2-bit encoding, between_words insertion).

```python
stego = secure_stego.secure_encode_simple(cover, secret, password)
```

##### `secure_decode_simple(stego_text, password)`

Decode with default parameters.

```python
message = secure_stego.secure_decode_simple(stego, password)
```

---

### IMAGE: B1 & B2 - LSB Steganography (image_stego.py)

**Complete LSB (Least Significant Bit) image steganography implementation.**

For detailed documentation, see [IMAGE_GUIDE.md](IMAGE_GUIDE.md)

#### Quick Start

```python
from image_stego import hide_message, extract_message

# Hide message in image
hide_message('photo.png', 'Secret message!', 'stego.png')

# Extract message
message = extract_message('stego.png')
```

#### B1: Basic LSB Functions

##### 1. `load_image(image_path) -> (pixels, format)`

Load an image and convert to numpy array.

```python
pixels, fmt = image_stego.load_image("photo.png")
# pixels = 3D array [height, width, 3 (RGB)]
```

**Supported formats:** PNG, BMP, TIFF (lossless formats only)

##### 2. `save_image(pixels, output_path, format='PNG')`

Save modified pixels as an image.

```python
image_stego.save_image(pixels, "output.png", "PNG")
```

##### 3. `encode_lsb(image_path, message, output_path, bits_per_pixel=1)`

**Main encoding function** - Hide message by modifying pixel LSBs.

```python
result = image_stego.encode_lsb(
    image_path="cover.png",
    message="Secret message to hide",
    output_path="stego.png",
    bits_per_pixel=1  # 1, 2, or 3
)

print(f"Encoded {result['message_length']} characters")
print(f"Capacity used: {result['capacity_used_percent']:.2f}%")
```

**How it works:**
1. Converts message to binary
2. Adds 32-bit header with message length
3. Modifies least significant bits of blue channel
4. Saves stego image (looks identical to original!)

##### 4. `decode_lsb(stego_image_path, bits_per_pixel=1)`

**Main decoding function** - Extract hidden message.

```python
message = image_stego.decode_lsb(
    stego_image_path="stego.png",
    bits_per_pixel=1  # Must match encoding!
)
```

**How it works:**
1. Reads LSBs from pixels
2. Extracts 32-bit header (message length)
3. Reads exact number of message bits
4. Converts back to text

##### 5. `get_image_capacity(image_path, bits_per_pixel=1)`

Check how many bytes can be hidden in an image.

```python
capacity = image_stego.get_image_capacity("photo.png", bits_per_pixel=1)
print(f"Can hide {capacity['max_characters']:,} characters")
# Example output: "Can hide 32,764 characters"
```

#### B2: Multi-Bit Capacity

**User-controlled capacity: 1, 2, or 3 bits per pixel**

| Bits/Pixel | Capacity | Visual Impact | Max Change |
|------------|----------|---------------|------------|
| **1** | Lowest | Invisible | ±1 |
| **2** | Medium ✓ Recommended | Nearly invisible | ±3 |
| **3** | Highest | Slightly visible | ±7 |

```python
# 1-bit: Maximum stealth (changes by ±1)
image_stego.encode_lsb(img, msg, out, bits_per_pixel=1)

# 2-bit: Balanced (RECOMMENDED, changes by ±3)
image_stego.encode_lsb(img, msg, out, bits_per_pixel=2)

# 3-bit: Maximum capacity (changes by ±7)
image_stego.encode_lsb(img, msg, out, bits_per_pixel=3)
```

**Important:** `bits_per_pixel` must match between encoding and decoding!

#### Message Length Header

**Automatic header system** stores message length in first 32 bits.

```
Image pixels: [Header: 32 bits][Message: N bits]
                    ↓
              Message length
```

**Benefits:**
- No need to specify message length when decoding
- Prevents reading garbage beyond message
- Supports messages up to 4GB (way more than images can hold!)

#### Simple API (Easiest)

```python
from image_stego import hide_message, extract_message

# Hide with quality settings
hide_message('photo.png', 'Secret!', 'stego.png', quality='standard')
# quality: 'high' (1 bit), 'standard' (2 bits), 'fast' (3 bits)

# Extract
message = extract_message('stego.png', quality='standard')
```

#### Utility Functions

##### Compare Images

```python
diff = image_stego.compare_images("original.png", "stego.png")
print(f"Max difference: {diff['max_difference']}")  # Should be 1, 3, or 7
print(f"Imperceptible: {diff['imperceptible']}")  # True if max ≤ 3
```

##### Create Test Image

```python
image_stego.create_test_image(512, 512, "test.png")
```

#### Example: Full Workflow

```python
import image_stego

# 1. Check capacity
capacity = image_stego.get_image_capacity("photo.png", bits_per_pixel=2)
print(f"Capacity: {capacity['max_characters']:,} characters")

# 2. Encode message
result = image_stego.encode_lsb(
    image_path="photo.png",
    message="This is my secret message!",
    output_path="stego.png",
    bits_per_pixel=2
)
print(f"Success! Used {result['capacity_used_percent']:.2f}% of capacity")

# 3. Verify encoding
decoded = image_stego.decode_lsb("stego.png", bits_per_pixel=2)
assert decoded == "This is my secret message!"

# 4. Compare images
diff = image_stego.compare_images("photo.png", "stego.png")
print(f"Images differ by max {diff['max_difference']} (imperceptible: {diff['imperceptible']})")
```

#### Capacity Examples

**Small image (256×256):**
- 1 bit/pixel: ~8,000 characters
- 2 bits/pixel: ~16,000 characters
- 3 bits/pixel: ~24,000 characters

**Medium image (512×512):**
- 1 bit/pixel: ~32,000 characters
- 2 bits/pixel: ~65,000 characters
- 3 bits/pixel: ~98,000 characters

**Large image (1920×1080 Full HD):**
- 1 bit/pixel: ~259,000 characters
- 2 bits/pixel: ~518,000 characters
- 3 bits/pixel: ~777,000 characters

---

## Complete Examples

### Example 1: Basic Steganography (No Encryption)

```python
import text_stego

cover = "The quick brown fox jumps over the lazy dog."
secret = "Hidden message"

# Encode
stego = text_stego.encode_message(cover, secret, encoding_bits=2)
print(f"Visible: {text_stego.get_visible_text(stego)}")
# Output: "The quick brown fox jumps over the lazy dog."

# Decode
decoded = text_stego.decode_message(stego, encoding_bits=2)
print(f"Secret: {decoded}")
# Output: "Hidden message"
```

### Example 2: Encrypted Steganography (Recommended)

```python
from secure_stego import secure_encode, secure_decode

cover = "Thanks for the book recommendation!"
secret = "The package is ready for pickup."
password = "dolphin-sunshine-2024"

# Alice encodes
stego = secure_encode(cover, secret, password)
# Stego looks like: "Thanks for the book recommendation!"
# But contains encrypted hidden message

# Bob decodes
message = secure_decode(stego, password)
print(message)  # "The package is ready for pickup."
```

### Example 3: Real-World Scenario

```python
from secure_stego import secure_encode, secure_decode
import text_stego

# Alice sends public message with hidden secret
public_message = "Looking forward to the conference next week!"
hidden_message = "Room 402, Building B, 9am sharp"
shared_password = "agent-alpha-7"

# Alice creates stego text
stego = secure_encode(public_message, hidden_message, shared_password)

# Alice posts to public forum
print(f"Public post: {text_stego.get_visible_text(stego)}")
# Output: "Looking forward to the conference next week!"
# (Looks completely normal)

# Bob receives and decodes
secret = secure_decode(stego, shared_password)
print(f"Hidden instruction: {secret}")
# Output: "Room 402, Building B, 9am sharp"

# If wrong password:
try:
    secure_decode(stego, "wrong_password")
except ValueError:
    print("Decryption failed - wrong password!")
```

### Example 4: Comparing Encoding Methods

```python
import secure_stego

cover = "Lorem ipsum dolor sit amet."
secret = "Test message"
password = "test123"

# Compare all methods
results = secure_stego.compare_methods(cover, secret, password)

for method, data in results.items():
    print(f"{method}: {data['zwc_count']} ZWC chars, "
          f"Success: {data['decode_success']}")
```

---

## Security Features

### 1. Encryption Layer

- **Algorithm**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Key Derivation**: SHA-256 hash of password
- **Random IV**: Unique initialization vector for each encryption
- **Authentication**: HMAC prevents tampering
- **Timestamp**: Built into Fernet token

### 2. Steganography Layer

- **Invisible Characters**: Completely invisible Unicode ZWC
- **Multiple Insertion Methods**: Distributes data to avoid detection
- **Efficient Encoding**: 2-bit mode reduces overhead by 50%
- **Zero Visual Impact**: Text appears completely normal

### 3. Defense-in-Depth

```
┌─────────────────────────────────────┐
│  Original Message                    │
└───────────┬─────────────────────────┘
            │
    ┌───────▼────────┐
    │  ENCRYPTION    │ ← First Layer of Protection
    │  (AES-128)     │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │  STEGANOGRAPHY │ ← Second Layer of Protection
    │  (ZWC Hiding)  │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │  Stego Text    │ ← Looks normal, contains encrypted secret
    └────────────────┘
```

**Security Guarantees:**
- If steganography is **not detected**: Message remains hidden
- If steganography **is detected**: Message is still encrypted
- Attacker needs to **break both** encryption AND detection

---

## Web API (D1, D2)

### Flask REST API Server

The project includes a complete Flask REST API for steganography operations. This makes it easy to integrate steganography into web applications, mobile apps, or use from any programming language that can make HTTP requests.

#### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/ping` | Health check - verify API is running |
| GET    | `/api/algorithms` | List all available algorithms and options |
| POST   | `/api/encode` | Hide message in text or image |
| POST   | `/api/decode` | Extract hidden message |
| POST   | `/api/analyze` | Calculate image quality metrics |

#### Quick Start

```bash
# Install dependencies (including Flask)
pip install -r requirements.txt

# Start the server
python app.py

# Server runs on http://localhost:5000
```

#### Example: Hide Message in Text (Python)

```python
import requests

url = "http://localhost:5000/api/encode"

payload = {
    "algorithm": "zwc",
    "cover_text": "Hello, how are you?",
    "secret_message": "Meet at noon",
    "password": "secretpass",
    "encoding_bits": 2
}

response = requests.post(url, json=payload)
result = response.json()

print("Stego text:", result['stego_text'])
print("Encrypted:", result['encrypted'])
```

#### Example: Analyze Image Quality

```python
import requests
import base64

# Read images
with open("original.png", "rb") as f:
    original = base64.b64encode(f.read()).decode('ascii')

with open("stego.png", "rb") as f:
    stego = base64.b64encode(f.read()).decode('ascii')

# Analyze
url = "http://localhost:5000/api/analyze"
response = requests.post(url, json={
    "original_image": original,
    "stego_image": stego
})

metrics = response.json()['metrics']
print(f"PSNR: {metrics['psnr']} dB")
print(f"SSIM: {metrics['ssim']}")
print(f"Quality: {metrics['quality_assessment']}")
```

#### Features

- **RESTful JSON API** - Clean, standard HTTP endpoints
- **Base64 Image Support** - Send/receive images as base64
- **Automatic Encryption** - Optional password parameter
- **Quality Analysis** - Built-in MSE, PSNR, SSIM metrics
- **Error Handling** - Detailed error messages with status codes
- **16MB File Limit** - Prevents abuse

#### Documentation

See **[API_GUIDE.md](API_GUIDE.md)** for:
- Complete API documentation
- Request/response examples
- Error handling guide
- Security best practices
- Production deployment tips
- cURL and Python examples

---

## Running Demos

### Demo 1: Basic ZWC Steganography

```bash
python demo.py
```

**Shows:**
- Text to binary conversion
- Binary to ZWC mapping (1-bit and 2-bit)
- Encoding with different insertion methods
- ZWC detection and analysis
- Efficiency comparison (1-bit vs 2-bit)

### Demo 2: Secure Encrypted Steganography

```bash
python demo_secure.py
```

**Shows:**
1. Encryption module demonstration
2. Secure encode pipeline (encrypt + hide)
3. Secure decode pipeline (extract + decrypt)
4. Wrong password security test
5. Simplified API usage
6. Method comparison
7. Defense-in-depth explanation
8. Real-world communication scenario

### Demo 3: LSB Image Steganography

```bash
python demo_image.py
```

**Shows:**
1. Image capacity calculator
2. Basic LSB encoding/decoding (B1)
3. Multi-bit capacity (1, 2, 3 bits per pixel) (B2)
4. Image comparison (visual impact analysis)
5. Simple API demonstration
6. Header system explanation
7. Capacity limits and error handling
8. Real-world communication scenario

**Creates:** Test images in `test_images/` directory

---

## Technical Details

### Unicode Characters Used

| Code Point | Character Name | 1-bit | 2-bit | Visibility |
|------------|----------------|-------|-------|------------|
| U+200B | Zero Width Space | - | `00` | Invisible |
| U+200C | Zero Width Non-Joiner | `0` | `01` | Invisible |
| U+200D | Zero Width Joiner | `1` | `10` | Invisible |
| U+FEFF | Zero Width No-Break Space | - | `11` | Invisible |

### Encoding Comparison

For a 6-character message "Secret" (48 bits):

| Encoding | ZWC Count | Efficiency | Use Case |
|----------|-----------|------------|----------|
| 1-bit | 48 chars | Standard | Simple implementation |
| 2-bit | 24 chars | **50% reduction** | Recommended for production |

### Encryption Overhead

For encrypted messages:
- **Salt**: 0 bytes (password-derived key)
- **IV**: 16 bytes (random per encryption)
- **HMAC**: 32 bytes (authentication)
- **Timestamp**: 8 bytes
- **Total overhead**: ~56 bytes + base64 encoding (~33% increase)

### Pipeline Diagrams

#### Encoding Pipeline

```
User Input ──┬──> Secret Message
             │
             └──> Password

             ↓

Step 1: ENCRYPT
    Secret Message + Password ──> AES-128 Encryption ──> Encrypted Data
                                                          (base64 token)
             ↓

Step 2: CONVERT TO BINARY
    Encrypted Data ──> text_to_binary() ──> Binary String
                                             (0s and 1s)
             ↓

Step 3: ENCODE AS ZWC
    Binary String ──> binary_to_zwc() ──> ZWC Characters
                      (2-bit encoding)     (invisible)
             ↓

Step 4: INSERT INTO COVER
    Cover Text + ZWC ──> encode_message() ──> Stego Text
                         (between_words)      (looks normal)
```

#### Decoding Pipeline

```
Stego Text + Password

             ↓

Step 1: EXTRACT ZWC
    Stego Text ──> zwc_to_binary() ──> Binary String
                                       (0s and 1s)
             ↓

Step 2: CONVERT TO TEXT
    Binary String ──> binary_to_text() ──> Encrypted Data
                                           (base64 token)
             ↓

Step 3: DECRYPT
    Encrypted Data + Password ──> AES-128 Decryption ──> Original Message
```

---

## Common Issues & Solutions

### Issue: "Decryption failed"

**Causes:**
1. Wrong password
2. Wrong `encoding_bits` (must match encoding value)
3. Stego text was modified

**Solution:**
```python
# Verify encoding_bits matches
stego = secure_encode(cover, secret, password, encoding_bits=2)
message = secure_decode(stego, password, encoding_bits=2)  # Must be 2!
```

### Issue: "Message looks corrupted"

**Cause:** Using wrong encoding_bits during decode

**Solution:**
```python
# If you don't remember encoding_bits, try both:
for bits in [1, 2]:
    try:
        message = secure_decode(stego, password, encoding_bits=bits)
        print(f"Success with {bits}-bit encoding!")
        break
    except:
        continue
```

---

## Best Practices

### 1. Password Security

```python
from crypto import verify_password_strength, generate_random_password

# Check password strength
strength = verify_password_strength("myPassword")
if strength['strength'] == 'Weak':
    print("Use a stronger password!")

# Or generate a strong one
strong_password = generate_random_password(20)
```

### 2. Always Use 2-bit Encoding

```python
# ✓ Good: 50% more efficient
stego = secure_encode(cover, secret, password, encoding_bits=2)

# ✗ Less efficient
stego = secure_encode(cover, secret, password, encoding_bits=1)
```

### 3. Choose Appropriate Insertion Method

```python
# For short cover text with many words:
method = 'between_words'  # ✓ Best distribution

# For long cover text:
method = 'distributed'  # ✓ Spreads evenly

# Simplest (but more detectable):
method = 'append'  # All ZWC at end
```

### 4. Verify Before Sending

```python
# Always test decode before sending
stego = secure_encode(cover, secret, password)

# Verify it works
decoded = secure_decode(stego, password, encoding_bits=2)
assert decoded == secret, "Encoding failed!"
```

---

## Performance Notes

### Space Requirements

For a message of N characters:
- Binary representation: N × 8 bits
- 1-bit encoding: N × 8 ZWC characters
- 2-bit encoding: N × 4 ZWC characters (recommended)

### Cover Text Requirements

Your cover text should be long enough to accommodate the hidden message comfortably.

**Rule of thumb:** Cover text should be at least 2× the length of the secret message for natural distribution.

---

## Future Enhancements (Not Yet Implemented)

These are part of the complete project roadmap:

- [ ] Image steganography (LSB, DCT, DWT methods)
- [ ] Web interface for easy use
- [ ] Steganalysis detection tools
- [ ] PBKDF2 key derivation with salt
- [ ] Support for file attachments
- [ ] Compression before encryption
- [ ] Multiple cover text formats

---

## Requirements

```
cryptography>=41.0.0
```

Python 3.7+ (uses `secrets` module and f-strings)

---

## Module Summary

| File | Purpose | Key Functions |
|------|---------|--------------|
| `text_stego.py` | ZWC encoder/decoder | `encode_message()`, `decode_message()` |
| `crypto.py` | Encryption | `encrypt_message()`, `decrypt_message()` |
| `secure_stego.py` | Secure pipeline | `secure_encode()`, `secure_decode()` |
| `demo.py` | Basic demo | - |
| `demo_secure.py` | Secure demo | - |

---

## License

Educational project for cryptography capstone course.

---

## Quick Reference Card

```python
# SECURE MODE (Recommended)
from secure_stego import secure_encode, secure_decode

# Encode
stego = secure_encode(cover_text, secret_message, password)

# Decode
message = secure_decode(stego, password)

# ────────────────────────────────────────────

# BASIC MODE (No encryption - not recommended)
import text_stego

# Encode
stego = text_stego.encode_message(cover, secret, encoding_bits=2)

# Decode
message = text_stego.decode_message(stego, encoding_bits=2)

# ────────────────────────────────────────────

# ANALYSIS
import text_stego

analysis = text_stego.analyze_text(stego)
print(analysis['has_hidden_data'])  # True/False
```

---

**For detailed examples, run the demos:**
- `python demo.py` - Basic ZWC steganography
- `python demo_secure.py` - Complete encrypted system
