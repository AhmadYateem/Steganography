# Image Quality Metrics Guide

## Quick Reference for MSE, PSNR, and SSIM

---

## What Are Quality Metrics?

Quality metrics help you measure how similar your stego image is to the original. The closer they are, the harder it is for someone to detect steganography!

**Think of it like this:**
- Original image = Your secret with no message hidden
- Stego image = Same image with hidden message
- Quality metrics = How well you hid the message (lower change = better hiding)

---

## The Three Metrics (C Requirements)

### 1. MSE (Mean Squared Error)

**What it is:** Average squared difference between pixels

**Formula:**
```
MSE = (1 / total_pixels) × Σ(original - stego)²
```

**How to read it:**
- **MSE = 0:** Perfect! Images are identical
- **MSE < 1:** Excellent (imperceptible differences)
- **MSE < 10:** Good
- **MSE > 100:** Poor (visible differences)

**Rule:** **Lower is better**

**Example:**
```python
from image_stego import calculate_mse

mse = calculate_mse("original.png", "stego.png")
print(f"MSE: {mse:.4f}")
# Output: MSE: 0.3251 (Excellent!)
```

---

### 2. PSNR (Peak Signal-to-Noise Ratio)

**What it is:** Quality measurement in decibels (dB)

**Formula:**
```
PSNR = 10 × log₁₀(255² / MSE)
```

**How to read it:**
- **PSNR > 50 dB:** Excellent (imperceptible)
- **PSNR 40-50 dB:** Very good
- **PSNR 30-40 dB:** Acceptable
- **PSNR < 30 dB:** Poor

**Rule:** **Higher is better**

**Example:**
```python
from image_stego import calculate_psnr

psnr = calculate_psnr("original.png", "stego.png")
print(f"PSNR: {psnr:.2f} dB")
# Output: PSNR: 52.15 dB (Excellent!)
```

---

### 3. SSIM (Structural Similarity Index)

**What it is:** How similar images look to human eyes

Considers:
- Luminance (brightness)
- Contrast
- Structure

**How to read it:**
- **SSIM = 1.0:** Perfect (identical images)
- **SSIM > 0.99:** Excellent
- **SSIM > 0.95:** Very good
- **SSIM > 0.90:** Good
- **SSIM < 0.90:** Poor

**Rule:** **Closer to 1.0 is better**

**Why it's special:** SSIM correlates better with human perception than MSE/PSNR!

**Example:**
```python
from image_stego import calculate_ssim

ssim = calculate_ssim("original.png", "stego.png")
print(f"SSIM: {ssim:.4f}")
# Output: SSIM: 0.9987 (Excellent!)
```

---

## All-In-One: Metrics Summary (RECOMMENDED)

Instead of calculating each metric separately, use the summary function:

```python
from image_stego import calculate_metrics_summary, print_metrics_report

# Calculate all metrics at once
metrics = calculate_metrics_summary("original.png", "stego.png")

# Print a nice report
print_metrics_report(metrics)
```

**Output:**
```
============================================================
  IMAGE QUALITY METRICS REPORT
============================================================

Metric               Value           Assessment
------------------------------------------------------------
MSE                  0.3251          Excellent (imperceptible differences)
PSNR                 52.15 dB        Excellent (imperceptible)
SSIM                 0.9987          Excellent (imperceptible)
------------------------------------------------------------

Overall Quality:     Excellent
Imperceptible:       Yes

Recommendations:
  1. Excellent quality! Changes are imperceptible.
============================================================
```

---

## Real-World Examples

### Example 1: Comparing Different Bit Settings

```python
import image_stego

cover = "photo.png"

# Test 1-bit, 2-bit, and 3-bit encoding
for bits in [1, 2, 3]:
    # Encode
    stego = f"stego_{bits}bit.png"
    image_stego.encode_lsb(cover, "Secret!", stego, bits_per_pixel=bits)

    # Calculate metrics
    mse = image_stego.calculate_mse(cover, stego)
    psnr = image_stego.calculate_psnr(cover, stego)
    ssim = image_stego.calculate_ssim(cover, stego)

    print(f"\n{bits}-bit encoding:")
    print(f"  MSE:  {mse:.4f}")
    print(f"  PSNR: {psnr:.2f} dB")
    print(f"  SSIM: {ssim:.4f}")
```

**Typical Output:**
```
1-bit encoding:
  MSE:  0.0003
  PSNR: 84.08 dB  ← Excellent!
  SSIM: 1.0000

2-bit encoding:
  MSE:  0.0066
  PSNR: 69.92 dB  ← Still excellent
  SSIM: 1.0000

3-bit encoding:
  MSE:  0.0227
  PSNR: 64.56 dB  ← Still very good
  SSIM: 1.0000
```

---

### Example 2: Before Sending, Check Quality

```python
import image_stego

# Create stego image
image_stego.hide_message("photo.png", "Secret message", "stego.png")

# Check quality before sending
metrics = image_stego.calculate_metrics_summary("photo.png", "stego.png")

if metrics['imperceptible']:
    print("✓ Safe to send! Changes are imperceptible.")
else:
    print("⚠️  Warning: Changes may be detectable!")
    print(f"Quality: {metrics['quality_assessment']}")

    # See recommendations
    for rec in metrics['recommendations']:
        print(f"  - {rec}")
```

---

### Example 3: Which is Better?

```python
import image_stego

cover = "original.png"

# Method A: 1-bit encoding
image_stego.encode_lsb(cover, "Secret", "method_a.png", bits_per_pixel=1)
metrics_a = image_stego.calculate_metrics_summary(cover, "method_a.png")

# Method B: 2-bit encoding
image_stego.encode_lsb(cover, "Secret", "method_b.png", bits_per_pixel=2)
metrics_b = image_stego.calculate_metrics_summary(cover, "method_b.png")

# Compare
print(f"Method A (1-bit): PSNR = {metrics_a['psnr']} dB")
print(f"Method B (2-bit): PSNR = {metrics_b['psnr']} dB")

if metrics_a['psnr'] > metrics_b['psnr']:
    print("→ Method A is better quality (but lower capacity)")
else:
    print("→ Method B is better quality")
```

---

## Quick Comparison Table

| Metric | What it measures | Good value | Bad value | Higher/Lower is better |
|--------|------------------|------------|-----------|------------------------|
| **MSE** | Average pixel difference² | < 1 | > 100 | **Lower** ⬇️ |
| **PSNR** | Quality in dB | > 50 dB | < 30 dB | **Higher** ⬆️ |
| **SSIM** | Human perception | > 0.99 | < 0.90 | **Closer to 1.0** ⬆️ |

---

## Common Patterns

### Excellent Quality (Imperceptible):
- MSE < 1
- PSNR > 50 dB
- SSIM > 0.99
- **Safe for steganography!** ✓

### Good Quality (Nearly Imperceptible):
- MSE < 10
- PSNR 40-50 dB
- SSIM > 0.95
- **Acceptable for most cases**

### Poor Quality (Detectable):
- MSE > 100
- PSNR < 30 dB
- SSIM < 0.90
- **Avoid! Changes are visible** ⚠️

---

## Tips for Better Quality

### 1. Use 1-bit encoding for maximum quality
```python
image_stego.encode_lsb(img, msg, out, bits_per_pixel=1)
# Higher PSNR, better SSIM
```

### 2. Choose larger cover images
```python
# Small image (256×256) with large message → Poor quality
# Large image (1920×1080) with same message → Excellent quality
```

### 3. Check before sending
```python
metrics = image_stego.calculate_metrics_summary(original, stego)
if not metrics['imperceptible']:
    print("Warning: Quality too low!")
    # Use different settings or larger image
```

### 4. Trust SSIM for human perception
```python
# SSIM is most reliable for how humans see the image
if metrics['ssim'] > 0.99:
    print("Humans won't notice the difference!")
```

---

## Implementation Details

### MSE Calculation:
```python
def calculate_mse(original_path, stego_path):
    # Load images
    orig_pixels = load_image(original_path)
    stego_pixels = load_image(stego_path)

    # Calculate squared differences
    squared_diff = (orig_pixels - stego_pixels) ** 2

    # Return average
    return np.mean(squared_diff)
```

### PSNR Calculation:
```python
def calculate_psnr(original_path, stego_path):
    mse = calculate_mse(original_path, stego_path)

    if mse == 0:
        return float('inf')  # Perfect quality

    # PSNR formula
    return 10 * np.log10(255² / mse)
```

### SSIM Calculation:
```python
def calculate_ssim(original_path, stego_path):
    # Uses scikit-image if available
    from skimage.metrics import structural_similarity as ssim

    orig = load_image(original_path)
    stego = load_image(stego_path)

    return ssim(orig, stego, channel_axis=2, data_range=255)
```

---

## When to Use Each Metric

### Use MSE when:
- You want a simple, quick check
- You're comparing many images
- You don't need human perception correlation

### Use PSNR when:
- You want industry-standard measurement
- Comparing with research papers
- Need a single number in dB

### Use SSIM when:
- **Most important:** You care how humans perceive the image
- Need most accurate quality assessment
- Want to match human judgment

### Use Summary when:
- **Recommended:** You want comprehensive assessment
- Need all three metrics
- Want automatic quality rating
- Need recommendations

---

## FAQ

**Q: Which metric is most important?**
A: SSIM is generally most important because it matches human perception best. But use all three for complete picture!

**Q: What's a "good enough" PSNR for steganography?**
A: PSNR > 40 dB is generally acceptable. PSNR > 50 dB is excellent.

**Q: Can metrics be 100% perfect?**
A: Yes! If MSE = 0, then PSNR = Infinite and SSIM = 1.0 (perfect match).

**Q: Why do I get different SSIM values?**
A: Make sure you have scikit-image installed for accurate SSIM. Without it, a fallback method is used which may differ slightly.

**Q: Which bits_per_pixel gives best metrics?**
A: 1-bit gives best quality (highest PSNR/SSIM), but lowest capacity. It's a tradeoff!

---

## Quick Reference Code

```python
# Install scikit-image for accurate SSIM
# pip install scikit-image

from image_stego import (
    calculate_mse,
    calculate_psnr,
    calculate_ssim,
    calculate_metrics_summary,
    print_metrics_report
)

# Individual metrics
mse = calculate_mse("original.png", "stego.png")
psnr = calculate_psnr("original.png", "stego.png")
ssim = calculate_ssim("original.png", "stego.png")

print(f"MSE:  {mse:.4f}")
print(f"PSNR: {psnr:.2f} dB")
print(f"SSIM: {ssim:.4f}")

# Or use summary (recommended)
metrics = calculate_metrics_summary("original.png", "stego.png")
print_metrics_report(metrics)
```

---

**For more details, see IMAGE_GUIDE.md**
