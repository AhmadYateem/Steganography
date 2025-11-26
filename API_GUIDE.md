# Steganography API Guide

Complete guide to using the Flask Web API for text and image steganography.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Running the Server](#running-the-server)
4. [API Endpoints](#api-endpoints)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [Security Best Practices](#security-best-practices)

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Server runs on http://localhost:5000
```

Test the server:
```bash
curl http://localhost:5000/ping
# Response: {"status":"ok","message":"Steganography API is running","version":"1.0.0"}
```

---

## Installation

### Requirements

- Python 3.7+
- Flask 3.0+
- cryptography
- Pillow (PIL)
- numpy
- scikit-image (optional, for accurate SSIM)

### Install All Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Flask cryptography Pillow numpy scikit-image
```

---

## Running the Server

### Development Mode (Debug Enabled)

```bash
python app.py
```

Output:
```
======================================================================
  STEGANOGRAPHY API SERVER
======================================================================

Available endpoints:
  GET  /ping              - Health check
  GET  /api/algorithms    - List available algorithms
  POST /api/encode        - Hide message in text/image
  POST /api/decode        - Extract hidden message
  POST /api/analyze       - Analyze image quality metrics

======================================================================
Starting server on http://localhost:5000
======================================================================

 * Running on http://0.0.0.0:5000
```

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## API Endpoints

### 1. Health Check

**GET `/ping`**

Check if the API is running.

**Request:**
```bash
curl http://localhost:5000/ping
```

**Response:**
```json
{
  "status": "ok",
  "message": "Steganography API is running",
  "version": "1.0.0"
}
```

---

### 2. List Algorithms

**GET `/api/algorithms`**

Get all available steganography algorithms.

**Request:**
```bash
curl http://localhost:5000/api/algorithms
```

**Response:**
```json
{
  "success": true,
  "algorithms": {
    "text": [
      {
        "id": "zwc",
        "name": "Zero-Width Characters (ZWC)",
        "description": "Hide messages using invisible Unicode characters",
        "encoding_bits": [1, 2],
        "insertion_methods": ["append", "between_words", "distributed"],
        "supports_encryption": true
      }
    ],
    "image": [
      {
        "id": "lsb",
        "name": "Least Significant Bit (LSB)",
        "description": "Hide messages in the least significant bits of image pixels",
        "bits_per_pixel": [1, 2, 3],
        "channels": ["blue", "green", "red"],
        "supports_encryption": true,
        "quality_metrics": ["MSE", "PSNR", "SSIM"]
      }
    ]
  },
  "total_count": 2
}
```

---

### 3. Encode Message

**POST `/api/encode`**

Hide a secret message in cover text or image.

#### Text Steganography (ZWC)

**Request:**
```json
POST /api/encode
Content-Type: application/json

{
  "algorithm": "zwc",
  "cover_text": "This is a public message that anyone can read.",
  "secret_message": "This is the hidden secret!",
  "password": "mypassword123",
  "encoding_bits": 2,
  "insertion_method": "between_words"
}
```

**Parameters:**
- `algorithm` (required): `"zwc"` for text steganography
- `cover_text` (required): Public text that will carry the hidden message
- `secret_message` (required): Secret message to hide
- `password` (optional): Encrypt message before hiding
- `encoding_bits` (optional): `1` or `2` (default: `2`)
- `insertion_method` (optional): `"append"`, `"between_words"`, or `"distributed"` (default: `"between_words"`)

**Response:**
```json
{
  "success": true,
  "message": "Message encoded successfully in text",
  "stego_text": "This​‌‍ is​‌‍ a​‌‍ public​‌‍ message...",
  "algorithm": "zwc",
  "encrypted": true,
  "encoding_bits": 2,
  "insertion_method": "between_words",
  "cover_length": 48,
  "stego_length": 62,
  "message_length": 26
}
```

#### Image Steganography (LSB)

**Request:**
```json
POST /api/encode
Content-Type: application/json

{
  "algorithm": "lsb",
  "cover_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "secret_message": "Hidden message in image",
  "password": "imagepass",
  "bits_per_pixel": 2,
  "channel": 2
}
```

**Parameters:**
- `algorithm` (required): `"lsb"` for image steganography
- `cover_image` (required): Base64-encoded image data
- `secret_message` (required): Secret message to hide
- `password` (optional): Encrypt message before hiding
- `bits_per_pixel` (optional): `1`, `2`, or `3` (default: `2`)
- `channel` (optional): `0` (red), `1` (green), or `2` (blue) (default: `2`)

**Response:**
```json
{
  "success": true,
  "message": "Message encoded successfully in image",
  "stego_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "algorithm": "lsb",
  "encrypted": true,
  "bits_per_pixel": 2,
  "channel": 2,
  "channel_name": "blue",
  "pixels_modified": 1024,
  "capacity_used_percent": 3.52,
  "message_length": 23
}
```

---

### 4. Decode Message

**POST `/api/decode`**

Extract hidden message from stego text or image.

#### Text Steganography (ZWC)

**Request:**
```json
POST /api/decode
Content-Type: application/json

{
  "algorithm": "zwc",
  "stego_text": "This​‌‍ is​‌‍ a​‌‍ public​‌‍ message...",
  "password": "mypassword123",
  "encoding_bits": 2
}
```

**Parameters:**
- `algorithm` (required): `"zwc"` for text steganography
- `stego_text` (required): Text containing hidden message
- `password` (optional): Decrypt message after extraction
- `encoding_bits` (optional): `1` or `2` (default: `2`)

**Response:**
```json
{
  "success": true,
  "message": "Message decoded successfully from text",
  "secret_message": "This is the hidden secret!",
  "algorithm": "zwc",
  "decrypted": true,
  "encoding_bits": 2,
  "message_length": 26
}
```

#### Image Steganography (LSB)

**Request:**
```json
POST /api/decode
Content-Type: application/json

{
  "algorithm": "lsb",
  "stego_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "password": "imagepass",
  "bits_per_pixel": 2,
  "channel": 2
}
```

**Parameters:**
- `algorithm` (required): `"lsb"` for image steganography
- `stego_image` (required): Base64-encoded stego image
- `password` (optional): Decrypt message after extraction
- `bits_per_pixel` (optional): `1`, `2`, or `3` (default: `2`)
- `channel` (optional): `0` (red), `1` (green), or `2` (blue) (default: `2`)

**Response:**
```json
{
  "success": true,
  "message": "Message decoded successfully from image",
  "secret_message": "Hidden message in image",
  "algorithm": "lsb",
  "decrypted": true,
  "bits_per_pixel": 2,
  "channel": 2,
  "channel_name": "blue",
  "message_length": 23
}
```

---

### 5. Analyze Image Quality

**POST `/api/analyze`**

Calculate quality metrics (MSE, PSNR, SSIM) between original and stego images.

**Request:**
```json
POST /api/analyze
Content-Type: application/json

{
  "original_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "stego_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Parameters:**
- `original_image` (required): Base64-encoded original image
- `stego_image` (required): Base64-encoded stego image

**Response:**
```json
{
  "success": true,
  "message": "Image quality analysis completed",
  "metrics": {
    "mse": 0.0066,
    "psnr": 69.92,
    "ssim": 1.0000,
    "quality_assessment": "Excellent",
    "imperceptible": true,
    "details": {
      "mse_interpretation": "Excellent (imperceptible differences)",
      "psnr_interpretation": "Excellent (imperceptible)",
      "ssim_interpretation": "Excellent (imperceptible)"
    },
    "recommendations": [
      "Excellent quality! Changes are imperceptible."
    ]
  }
}
```

---

## Examples

### Example 1: Hide Message in Text (Python)

```python
import requests
import json

url = "http://localhost:5000/api/encode"

payload = {
    "algorithm": "zwc",
    "cover_text": "Hello, how are you today?",
    "secret_message": "Meet at noon",
    "password": "secretpass",
    "encoding_bits": 2
}

response = requests.post(url, json=payload)
result = response.json()

print("Stego text:", result['stego_text'])
print("Encrypted:", result['encrypted'])
```

### Example 2: Extract Message from Text (Python)

```python
import requests

url = "http://localhost:5000/api/decode"

payload = {
    "algorithm": "zwc",
    "stego_text": "Hello,​‌‍ how​‌‍ are​‌‍ you​‌‍ today?",
    "password": "secretpass",
    "encoding_bits": 2
}

response = requests.post(url, json=payload)
result = response.json()

print("Secret message:", result['secret_message'])
# Output: Meet at noon
```

### Example 3: Hide Message in Image (Python)

```python
import requests
import base64

# Read image and encode to base64
with open("photo.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('ascii')

url = "http://localhost:5000/api/encode"

payload = {
    "algorithm": "lsb",
    "cover_image": image_data,
    "secret_message": "Top secret information",
    "password": "imagekey",
    "bits_per_pixel": 1  # Best quality
}

response = requests.post(url, json=payload)
result = response.json()

# Save stego image
stego_image_data = base64.b64decode(result['stego_image'])
with open("stego.png", "wb") as f:
    f.write(stego_image_data)

print(f"Capacity used: {result['capacity_used_percent']:.2f}%")
```

### Example 4: Analyze Image Quality (Python)

```python
import requests
import base64

# Read both images
with open("original.png", "rb") as f:
    original = base64.b64encode(f.read()).decode('ascii')

with open("stego.png", "rb") as f:
    stego = base64.b64encode(f.read()).decode('ascii')

url = "http://localhost:5000/api/analyze"

payload = {
    "original_image": original,
    "stego_image": stego
}

response = requests.post(url, json=payload)
result = response.json()

metrics = result['metrics']
print(f"MSE:  {metrics['mse']}")
print(f"PSNR: {metrics['psnr']} dB")
print(f"SSIM: {metrics['ssim']}")
print(f"Quality: {metrics['quality_assessment']}")
print(f"Imperceptible: {metrics['imperceptible']}")
```

### Example 5: Using cURL

**List algorithms:**
```bash
curl http://localhost:5000/api/algorithms
```

**Encode text message:**
```bash
curl -X POST http://localhost:5000/api/encode \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "zwc",
    "cover_text": "Public message",
    "secret_message": "Secret!"
  }'
```

**Decode text message:**
```bash
curl -X POST http://localhost:5000/api/decode \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "zwc",
    "stego_text": "Public​‌‍ message"
  }'
```

---

## Error Handling

### Error Response Format

All errors return JSON with `success: false`:

```json
{
  "error": "Error message here",
  "success": false
}
```

### Common Errors

#### 400 Bad Request
- Missing required parameters
- Invalid algorithm name
- Invalid encoding_bits or bits_per_pixel values
- Invalid base64 image data

**Example:**
```json
{
  "error": "'secret_message' is required",
  "success": false
}
```

#### 401 Unauthorized
- Wrong password during decryption

**Example:**
```json
{
  "error": "Decryption failed (wrong password?): ...",
  "success": false
}
```

#### 413 Request Entity Too Large
- File exceeds 16MB limit

**Example:**
```json
{
  "error": "File too large (max 16MB)",
  "success": false
}
```

#### 404 Not Found
- Endpoint doesn't exist

**Example:**
```json
{
  "error": "Endpoint not found",
  "success": false
}
```

#### 500 Internal Server Error
- Unexpected server error

**Example:**
```json
{
  "error": "Internal server error",
  "success": false
}
```

---

## Security Best Practices

### 1. Always Use Passwords for Sensitive Data

```python
# Good: Encrypted
payload = {
    "algorithm": "lsb",
    "cover_image": image_data,
    "secret_message": "Sensitive info",
    "password": "strong_password_123"  # ✓ Encrypted
}

# Bad: No encryption
payload = {
    "algorithm": "lsb",
    "cover_image": image_data,
    "secret_message": "Sensitive info"  # ✗ Anyone can extract
}
```

### 2. Use Strong Passwords

```python
# Good
password = "MyStr0ng!P@ssw0rd#2024"

# Bad
password = "123456"
```

### 3. Use HTTPS in Production

```bash
# Development (OK for local testing)
http://localhost:5000/api/encode

# Production (MUST use HTTPS)
https://your-domain.com/api/encode
```

### 4. Validate Image Quality

Always check metrics after encoding:

```python
# Encode image
encode_response = requests.post(url, json=encode_payload)
stego_image = encode_response.json()['stego_image']

# Analyze quality
analyze_response = requests.post(
    "http://localhost:5000/api/analyze",
    json={
        "original_image": original_image,
        "stego_image": stego_image
    }
)

metrics = analyze_response.json()['metrics']

if not metrics['imperceptible']:
    print("⚠️  Warning: Changes may be visible!")
    print(f"PSNR: {metrics['psnr']} dB (should be > 50)")
else:
    print("✓ Safe to use - imperceptible changes")
```

### 5. Choose Appropriate Settings

**For maximum security (imperceptible):**
```python
{
    "bits_per_pixel": 1,  # Lowest capacity, best quality
    "password": "strong_password"
}
```

**For balanced approach:**
```python
{
    "bits_per_pixel": 2,  # Recommended
    "password": "strong_password"
}
```

**For maximum capacity (may be visible):**
```python
{
    "bits_per_pixel": 3,  # Highest capacity, lower quality
    "password": "strong_password"
}
```

---

## Rate Limiting & Production Deployment

### Rate Limiting (Recommended)

Install Flask-Limiter:
```bash
pip install Flask-Limiter
```

Add to `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"]
)
```

### Production Deployment

Use Gunicorn + Nginx:

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'Flask'"

**Solution:**
```bash
pip install Flask
# or
pip install -r requirements.txt
```

### Issue: "Decryption failed (wrong password?)"

**Solution:**
- Ensure password matches between encode and decode
- Password is case-sensitive

### Issue: "Message too large for image capacity"

**Solution:**
- Use larger image
- Use higher bits_per_pixel (2 or 3)
- Compress or shorten message

### Issue: "Invalid base64 image data"

**Solution:**
- Ensure image is properly base64-encoded
- Remove `data:image/png;base64,` prefix if present (or keep it - API handles both)

---

## Summary

**Quick API Reference:**

```
GET  /ping                    → Health check
GET  /api/algorithms          → List algorithms
POST /api/encode              → Hide message (text or image)
POST /api/decode              → Extract message
POST /api/analyze             → Calculate image quality metrics
```

**Algorithms:**
- `zwc` - Zero-Width Characters (text steganography)
- `lsb` - Least Significant Bit (image steganography)

**For more details:**
- See `USAGE_GUIDE.md` for text steganography
- See `IMAGE_GUIDE.md` for image steganography
- See `METRICS_GUIDE.md` for quality metrics
