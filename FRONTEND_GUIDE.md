# Steganography Suite - Frontend Guide

## 🎨 Modern, Apple-Level Professional Interface

A stunning, production-ready frontend for the Steganography Suite with professional design, smooth animations, and excellent UX.

---

## Features

### 🎯 Core Functionality
- **Text Steganography** - Hide messages in invisible Unicode characters
- **Image Steganography** - Hide messages in image pixels using LSB
- **Encryption Support** - Optional password protection for all operations
- **Real-time Quality Metrics** - Live MSE, PSNR, and SSIM analysis
- **Image Preview** - Side-by-side comparison of original and stego images

### ✨ Design Excellence
- **Apple-Inspired Design** - Clean, minimal, professional aesthetic
- **Smooth Animations** - Thoughtful micro-interactions throughout
- **Professional Typography** - San Francisco-like font stack
- **Dark Mode UI** - Modern dark interface with subtle gradients
- **Responsive Layout** - Works beautifully on all screen sizes
- **Visual Feedback** - Color-coded metrics and status indicators

### 🚀 User Experience
- **Drag & Drop** - Intuitive file upload
- **Toast Notifications** - Non-intrusive success/error messages
- **Loading States** - Clear feedback during API calls
- **Copy to Clipboard** - One-click result copying
- **Download Images** - Easy stego image download
- **Keyboard Accessible** - Full keyboard navigation support

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask 3.0+
- Flask-CORS 4.0+ (for API access)
- All steganography dependencies

### 2. Start the Server

```bash
python app.py
```

Server starts on: **http://localhost:5000**

### 3. Open in Browser

Navigate to: **http://localhost:5000**

---

## Using the Interface

### Text Steganography

1. **Click "Text Steganography" tab**
2. **Enter cover text** - Public message visible to everyone
3. **Enter secret message** - Hidden message
4. **Optional: Add password** - Encrypts the secret message
5. **Choose encoding bits** - 1 or 2 (2 recommended)
6. **Click "Encode Message"** - Creates stego text
7. **Copy result** - Stego text looks normal but contains hidden message

**To Decode:**
1. Paste stego text in "Cover Text" field
2. Enter password (if used)
3. Click "Decode Message"
4. Secret message appears in results

### Image Steganography

1. **Click "Image Steganography" tab**
2. **Upload image** - Click or drag & drop PNG/JPG/BMP
3. **Enter secret message** - Message to hide
4. **Optional: Add password** - Encrypts the message
5. **Choose settings:**
   - **Bits per pixel:** 1 (best quality), 2 (balanced), 3 (max capacity)
   - **Channel:** Red, Green, or Blue (Blue recommended)
6. **Click "Encode Image"**
7. **View results:**
   - Quality metrics (MSE, PSNR, SSIM)
   - Side-by-side image comparison
   - Download stego image

**To Decode:**
1. Upload stego image
2. Enter password (if used)
3. Match encoding settings (bits per pixel, channel)
4. Click "Decode Image"
5. Secret message appears in results

---

## Understanding Quality Metrics

### MSE (Mean Squared Error)
**Lower is better**

| Value | Quality | Visual |
|-------|---------|--------|
| 0 | Perfect | Identical |
| < 1 | Excellent | Imperceptible |
| < 10 | Good | Nearly imperceptible |
| > 100 | Poor | Visible differences |

**Color Code:**
- 🟢 Green = Excellent
- 🔵 Blue = Good
- 🟡 Yellow = Acceptable
- 🔴 Red = Poor

### PSNR (Peak Signal-to-Noise Ratio)
**Higher is better** (measured in dB)

| Value | Quality | Visual |
|-------|---------|--------|
| ∞ (Infinite) | Perfect | Identical |
| > 50 dB | Excellent | Imperceptible |
| 40-50 dB | Very Good | Nearly imperceptible |
| 30-40 dB | Acceptable | Minor differences |
| < 30 dB | Poor | Visible differences |

### SSIM (Structural Similarity Index)
**Closer to 1.0 is better**

| Value | Quality | Visual |
|-------|---------|--------|
| 1.0 | Perfect | Identical |
| > 0.99 | Excellent | Imperceptible to humans |
| > 0.95 | Very Good | Nearly imperceptible |
| > 0.90 | Good | Minor differences |
| < 0.90 | Poor | Noticeable differences |

**Why SSIM matters:** SSIM correlates better with human perception than MSE/PSNR, making it the most important metric for steganography.

---

## Design System

### Color Palette

```
Background:        #0a0a0f (Deep dark)
Surface:           #1a1a24 (Card background)
Surface Elevated:  #24243a (Input backgrounds)
Primary:           #007aff (Apple blue)
Accent:            #5e5ce6 (Purple accent)
Success:           #30d158 (Green)
Warning:           #ff9f0a (Orange)
Error:             #ff453a (Red)
```

### Typography

**Font Stack:**
```
-apple-system, BlinkMacSystemFont, 'SF Pro Display',
'Segoe UI', 'Inter', system-ui, sans-serif
```

**Sizes:**
- Title: 3.5rem (56px)
- Subtitle: 1.25rem (20px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)

### Spacing Scale

```
XS:  0.5rem  (8px)
SM:  0.75rem (12px)
MD:  1rem    (16px)
LG:  1.5rem  (24px)
XL:  2rem    (32px)
2XL: 3rem    (48px)
```

### Border Radius

```
SM:  8px
MD:  12px
LG:  16px
XL:  24px
```

---

## Animations & Transitions

### Page Load Sequence
1. Header fades in from top (0.8s)
2. Mode switcher fades in (0.8s, 0.2s delay)
3. Main card fades in from bottom (0.8s, 0.3s delay)
4. Background gradient shifts continuously

### Interactions
- **Buttons:** Lift on hover (-2px translate)
- **Cards:** Subtle lift and shadow on hover
- **Mode switch:** Content cross-fades smoothly
- **Form inputs:** Glow effect on focus
- **File upload:** Scale up on drag-over

### Timing
- Fast: 150ms (micro-interactions)
- Base: 250ms (standard transitions)
- Slow: 400ms (mode switching)

---

## Browser Support

✅ **Fully Supported:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

⚠️ **Partial Support:**
- IE 11 (degraded experience, no animations)

---

## Performance Optimizations

1. **Single File Application** - No external dependencies
2. **CSS Variables** - Fast theme switching capability
3. **Hardware Acceleration** - Transform-based animations
4. **Efficient Selectors** - Optimized CSS specificity
5. **Lazy Image Loading** - Images only loaded when needed
6. **Debounced Inputs** - Prevents excessive API calls

---

## Customization

### Changing Colors

Edit CSS variables in `:root` section:

```css
:root {
    --color-primary: #007aff;  /* Change primary color */
    --color-accent: #5e5ce6;   /* Change accent color */
    /* ... */
}
```

### Changing API Endpoint

Edit JavaScript configuration:

```javascript
const API_BASE_URL = 'http://your-api-url.com';
```

### Adding Dark/Light Mode Toggle

The interface is dark by default. To add light mode:

1. Create a new `:root.light` theme
2. Add toggle button in header
3. Use JavaScript to switch classes

---

## Troubleshooting

### Issue: API calls fail with CORS error

**Solution:**
```bash
pip install Flask-CORS
```

Ensure `app.py` has:
```python
from flask_cors import CORS
CORS(app)
```

### Issue: Images not uploading

**Causes:**
- File too large (>16MB limit)
- Invalid format (use PNG, JPG, or BMP)

**Solution:**
- Compress image before uploading
- Convert to supported format

### Issue: Metrics show "Poor" quality

**Causes:**
- Using 3 bits per pixel
- Very small image with large message
- Wrong channel selected

**Solution:**
- Use 1 or 2 bits per pixel
- Use larger cover image
- Try different channel (Blue recommended)

---

## Accessibility

### Keyboard Navigation
- `Tab` - Navigate between fields
- `Enter` - Activate buttons
- `Esc` - Close modals/toasts
- `Space` - Toggle switches

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on interactive elements
- Alt text on images
- Status announcements for async operations

### Visual Accessibility
- High contrast ratios (WCAG AA compliant)
- Focus indicators on all interactive elements
- Color not sole indicator (text + color)
- Large touch targets (44x44px minimum)

---

## Security Best Practices

### When Using the Interface

1. **Always use passwords** for sensitive data
2. **Use HTTPS** in production (not HTTP)
3. **Clear browser cache** after sensitive operations
4. **Don't share stego files** without encryption
5. **Verify metrics** before sharing images

### For Developers

1. **Never log passwords** in console
2. **Sanitize inputs** before API calls
3. **Validate file types** before upload
4. **Clear sensitive data** from memory
5. **Use CSP headers** in production

---

## Production Deployment

### Nginx Configuration

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

### SSL/HTTPS Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### Environment Variables

```bash
export FLASK_ENV=production
export API_BASE_URL=https://your-domain.com
```

---

## Future Enhancements

Potential improvements for the interface:

- [ ] Light mode toggle
- [ ] Batch processing for multiple images
- [ ] Progress bars for large files
- [ ] History of recent operations
- [ ] Export settings as JSON
- [ ] Keyboard shortcuts panel
- [ ] Mobile app version
- [ ] Multi-language support

---

## Credits

**Design Inspiration:**
- Apple Human Interface Guidelines
- Material Design 3
- Tailwind CSS

**Icons:**
- Emoji (Unicode)

**Fonts:**
- System fonts (no external dependencies)

---

## License

Part of the Steganography Suite project.

---

## Support

For issues or questions:
1. Check this guide
2. See API_GUIDE.md for API details
3. Review console for error messages
4. Report issues with screenshots

---

**Enjoy your beautiful steganography interface! ✨**
