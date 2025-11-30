"""Quick test to debug detector issue"""
import base64
import io
from PIL import Image
from features import StegoDetector

# Create test image
img = Image.new('RGB', (400, 300), color=(100, 150, 200))
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_data = buffer.getvalue()

print("Testing StegoDetector.analyze_image()...")
try:
    result = StegoDetector.analyze_image(image_data)
    print("SUCCESS!")
    print(f"Probability: {result['has_stego_probability']}%")
    print(f"Verdict: {result['verdict']}")
    print(f"Indicators: {result['indicators']}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
