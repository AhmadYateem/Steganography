# Quick Usage Guide

## For Users Who Want to Get Started Fast

### Installation

```bash
cd Steganography
pip install -r requirements.txt
```

### Simplest Usage (3 lines of code)

```python
from secure_stego import secure_encode_simple, secure_decode_simple

# Hide a secret message
stego = secure_encode_simple("Normal visible text", "Secret message", "password123")

# Extract the secret message
secret = secure_decode_simple(stego, "password123")
print(secret)  # "Secret message"
```

That's it! The text looks normal but contains an encrypted hidden message.

---

## What Each Module Does

### For Understanding the Code Later

```
text_stego.py     ← Basic steganography (no encryption)
                    - Hides text using invisible Unicode characters
                    - encode_message() and decode_message()

crypto.py         ← Encryption only
                    - Encrypts text with password (AES-128)
                    - encrypt_message() and decrypt_message()

secure_stego.py   ← BOTH combined (USE THIS!)
                    - Encrypts THEN hides
                    - secure_encode() and secure_decode()
                    - Most secure option
```

---

## A1, A2, A3 Requirements Mapping

### A1: ZWC Encoder ✓
Located in `text_stego.py`:
- `text_to_binary()` - converts text to 0s and 1s
- `binary_to_zwc()` - maps binary to invisible characters
- `encode_message()` - hides invisible characters in cover text

### A2: ZWC Decoder ✓
Located in `text_stego.py`:
- `zwc_to_binary()` - reads invisible characters back
- `decode_message()` - extracts hidden message

### A3: Encryption Around Text Hiding ✓
Located in `crypto.py` + `secure_stego.py`:
- `crypto.encrypt_message()` - AES encryption with password
- `crypto.decrypt_message()` - AES decryption with password
- `secure_stego.secure_encode()` - FULL PIPELINE: encrypt → hide
- `secure_stego.secure_decode()` - FULL PIPELINE: extract → decrypt

---

## How the Pipelines Work

### Encode Pipeline (User enters message + password)

```
Secret Message ──────┐
                     ├──> ENCRYPT ──> CONVERT TO BINARY ──> MAP TO ZWC ──> INSERT IN COVER TEXT
Password ────────────┘
```

Result: Text that looks normal but contains encrypted secret

### Decode Pipeline (Extract from stego text + password)

```
Stego Text ──────────┐
                     ├──> EXTRACT ZWC ──> CONVERT TO BINARY ──> DECRYPT ──> Original Message
Password ────────────┘
```

---

## Common Use Cases

### Case 1: I want maximum security

```python
from secure_stego import secure_encode, secure_decode

# Encode with encryption
stego = secure_encode(
    cover_text="Public message here",
    secret_message="Actual secret",
    password="strong_password_123",
    encoding_bits=2,  # More efficient
    insertion_method='between_words'  # More distributed
)

# Decode
secret = secure_decode(stego, "strong_password_123", encoding_bits=2)
```

### Case 2: I just want to test it quickly

```python
from secure_stego import secure_encode_simple, secure_decode_simple

stego = secure_encode_simple("Hello world", "Secret", "pass123")
secret = secure_decode_simple(stego, "pass123")
```

### Case 3: I want to see how it works (no encryption)

```python
import text_stego

# Basic hiding (not encrypted)
stego = text_stego.encode_message("Cover text", "Secret", encoding_bits=2)
secret = text_stego.decode_message(stego, encoding_bits=2)
```

### Case 4: I want to check if text has hidden data

```python
import text_stego

analysis = text_stego.analyze_text(suspicious_text)

if analysis['has_hidden_data']:
    print(f"Found {analysis['zwc_chars']} hidden characters!")
else:
    print("No hidden data detected")
```

---

## Running the Demos

### See everything in action:

```bash
# Basic steganography demo
python demo.py

# Full encrypted steganography demo
python demo_secure.py
```

---

## Important Notes

1. **encoding_bits must match**: If you encode with `encoding_bits=2`, you MUST decode with `encoding_bits=2`
2. **Password must match**: Wrong password = decryption fails
3. **Use 2-bit encoding**: It's 50% more efficient than 1-bit
4. **Recommended mode**: Always use `secure_encode()` / `secure_decode()` for real use

---

## Troubleshooting

**Error: "Decryption failed"**
- Check password is correct
- Check encoding_bits matches (1 or 2)

**Message looks corrupted**
- You probably used wrong encoding_bits during decode
- Try both `encoding_bits=1` and `encoding_bits=2`

**Want to see if hiding worked?**
```python
visible = text_stego.get_visible_text(stego)
print(visible)  # Should look normal
```

---

## File Organization

```
├── text_stego.py          → A1 & A2 implementation
├── crypto.py              → A3 encryption implementation
├── secure_stego.py        → A3 full pipeline (MAIN API)
├── demo.py                → Basic demo
├── demo_secure.py         → Full demo with encryption
├── README.md              → Complete documentation
├── USAGE_GUIDE.md         → This file
└── requirements.txt       → Dependencies
```

---

**For full documentation, see README.md**
**For code examples, run demo_secure.py**
