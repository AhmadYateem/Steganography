"""Test detector API endpoint directly"""
import requests
import base64
import io
from PIL import Image

# Create test image
img = Image.new('RGB', (400, 300), color=(100, 150, 200))
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_b64 = base64.b64encode(buffer.getvalue()).decode('ascii')

# Test API
url = "http://localhost:5000/api/detect/image"
response = requests.post(url, json={'image': image_b64})

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nSuccess!")
    print(f"Probability: {data.get('analysis', {}).get('has_stego_probability')}%")
else:
    print(f"\nError!")
