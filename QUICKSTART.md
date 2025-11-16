# 🚀 Quick Start Guide

Get the Steganography Suite running in 60 seconds!

---

## Super Quick Start (3 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web server)
- Flask-CORS (API access)
- cryptography (encryption)
- Pillow + numpy (image processing)
- scikit-image (quality metrics)

### 2. Start the Server

**Option A: Python (Works Everywhere)**
```bash
python app.py
```

**Option B: Cross-Platform Launcher (Recommended)**
```bash
python start.py
```

**Option C: Platform-Specific Scripts**

*Linux/Mac:*
```bash
./start.sh
```

*Windows:*
```bash
start.bat
```

Or double-click `start.bat` in File Explorer

### 3. Open Your Browser

Navigate to: **http://localhost:5000**

🎉 **That's it!** You should see the beautiful interface.

---

## What You'll See

### Text Steganography Tab
- Enter cover text (public message)
- Enter secret message (hidden message)
- Optional: Add password for encryption
- Click "Encode Message"
- Copy the result - it looks normal but contains your secret!

### Image Steganography Tab
- Drag & drop an image (or click to upload)
- Enter secret message
- Optional: Add password
- Click "Encode Image"
- See quality metrics (MSE, PSNR, SSIM)
- Compare original vs stego image
- Download the stego image

---

## First Test

### Try This Simple Example

1. **Go to Text Steganography tab**

2. **Cover Text:**
   ```
   Hello! Hope you're having a great day. Looking forward to our meeting tomorrow.
   ```

3. **Secret Message:**
   ```
   The package arrives at midnight
   ```

4. **Password:** (optional)
   ```
   secret123
   ```

5. **Click "Encode Message"**

6. **Copy the result** - it looks exactly like your cover text!

7. **To decode:** Paste the stego text back into "Cover Text", enter the same password, and click "Decode Message"

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install Flask Flask-CORS
```

### "ModuleNotFoundError: No module named 'flask_cors'"

**Solution:**
```bash
pip install Flask-CORS
```

### Port 5000 already in use

**Solution:**
Edit `app.py` and change the last line:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changed from 5000 to 8080
```

Then visit: http://localhost:8080

### CORS errors in browser console

**Solution:**
Ensure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

And verify `app.py` has:
```python
from flask_cors import CORS
CORS(app)
```

### Images not uploading

**Check:**
- File is PNG, JPG, or BMP
- File is less than 16MB
- Try a different image

---

## Next Steps

### Learn More

- **[README.md](README.md)** - Complete project overview
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Frontend documentation
- **[API_GUIDE.md](API_GUIDE.md)** - API documentation
- **[IMAGE_GUIDE.md](IMAGE_GUIDE.md)** - Image steganography guide
- **[METRICS_GUIDE.md](METRICS_GUIDE.md)** - Quality metrics explained

### Try Advanced Features

1. **Password Encryption**
   - Always use passwords for sensitive data
   - Adds AES-128-CBC encryption layer
   - Provides defense-in-depth security

2. **Different Encoding Settings**
   - **Text:** Try 1-bit vs 2-bit encoding
   - **Image:** Try 1, 2, or 3 bits per pixel
   - Compare quality metrics

3. **Quality Analysis**
   - Check PSNR > 50 dB = Excellent
   - Check SSIM > 0.99 = Imperceptible
   - Use metrics to verify steganography quality

### Use the API Directly

If you want to integrate steganography into your own app:

```python
import requests

# Encode text
response = requests.post('http://localhost:5000/api/encode', json={
    'algorithm': 'zwc',
    'cover_text': 'Public message',
    'secret_message': 'Secret!',
    'password': 'mypass'
})

stego_text = response.json()['stego_text']
```

See [API_GUIDE.md](API_GUIDE.md) for more examples.

---

## Demo Videos

### Text Steganography Demo

1. Switch to "Text Steganography" tab
2. Enter cover text
3. Enter secret message
4. Click "Encode"
5. See result with invisible characters
6. Copy and paste to decode

### Image Steganography Demo

1. Switch to "Image Steganography" tab
2. Upload an image (drag & drop works!)
3. Enter secret message
4. Click "Encode Image"
5. See quality metrics dashboard
6. Compare original vs stego images
7. Download stego image
8. Upload stego image to decode

---

## Tips for Best Results

### For Text Steganography

✅ **Do:**
- Use longer cover texts (more room for hiding)
- Use 2-bit encoding (50% more efficient)
- Always use passwords for sensitive data
- Test decode immediately after encode

❌ **Don't:**
- Use very short cover texts (< 20 characters)
- Forget the password (can't decode without it!)
- Copy only part of the stego text

### For Image Steganography

✅ **Do:**
- Use larger images (more capacity)
- Use 1-bit for maximum quality
- Use 2-bit for balanced approach (recommended)
- Check PSNR > 50 dB before sharing
- Always use passwords for sensitive data

❌ **Don't:**
- Use tiny images with large messages
- Use 3-bit if image quality is critical
- Compress stego images (destroys hidden data!)
- Convert to JPEG (lossy compression breaks it)

---

## System Requirements

### Minimum

- Python 3.7+
- 2GB RAM
- Modern browser (Chrome, Firefox, Safari, Edge)

### Recommended

- Python 3.9+
- 4GB RAM
- Chrome 90+ or Firefox 88+
- 1920x1080 display for best UI experience

---

## Security Notes

⚠️ **Important:**

1. **Always use HTTPS in production** (not HTTP)
2. **Never share passwords** through insecure channels
3. **Verify quality metrics** before sharing stego images
4. **Keep stego files secure** until delivered
5. **Use strong passwords** (12+ characters)

---

## Support

### Getting Help

1. Check this guide first
2. Read [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for interface help
3. Read [API_GUIDE.md](API_GUIDE.md) for API help
4. Check browser console for errors (F12 → Console)

### Reporting Issues

Include:
- Python version (`python --version`)
- Operating system
- Error message (if any)
- Steps to reproduce
- Browser console errors

---

## What Makes This Special?

### 🎨 Design

- **Apple-inspired** professional interface
- **Smooth animations** and micro-interactions
- **Dark theme** with subtle gradients
- **Professional typography** (San Francisco-like fonts)
- **Responsive design** works on all devices

### 🚀 Performance

- **Single-file app** (no build step needed)
- **Fast loading** (< 1 second)
- **Smooth animations** (60 FPS)
- **Efficient code** (vanilla JavaScript)

### 🔒 Security

- **AES-128 encryption** with HMAC
- **Defense-in-depth** (encryption + steganography)
- **Password protection** for all operations
- **Secure by default** design

### 📊 Features

- **Real-time metrics** (MSE, PSNR, SSIM)
- **Visual feedback** (color-coded status)
- **Drag & drop** file upload
- **Side-by-side** image comparison
- **One-click** download

---

**Ready to hide some secrets? Let's go! 🚀**

Open **http://localhost:5000** in your browser and enjoy the beautiful interface!
