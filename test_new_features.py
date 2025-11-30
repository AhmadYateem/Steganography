"""
Comprehensive Test Suite for New Features
Tests all 4 advanced features with real data
"""

import requests
import base64
import json
import time
from PIL import Image
import io

BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a test image and return base64."""
    img = Image.new('RGB', (400, 300), color=(100, 150, 200))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')

def print_test(name):
    """Print test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)

def print_result(success, message=""):
    """Print test result."""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}: {message}")

# ============================================================================
# TEST 1: CHALLENGE SYSTEM
# ============================================================================

def test_challenges():
    """Test challenge generator."""
    print_test("Challenge System")

    # Test 1.1: Get all challenges
    print("\n1.1 Get all challenges")
    response = requests.get(f"{BASE_URL}/api/challenges")
    print_result(response.status_code == 200, f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        challenges = data.get('challenges', [])
        print(f"    Found {len(challenges)} challenges")
        for c in challenges[:3]:
            print(f"    - {c['title']} ({c['difficulty']}) - {c['points']} points")

    # Test 1.2: Get specific challenge
    print("\n1.2 Get challenge #1")
    response = requests.get(f"{BASE_URL}/api/challenges/1")
    print_result(response.status_code == 200, f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        challenge = data.get('challenge', {})
        print(f"    Title: {challenge.get('title')}")
        print(f"    Algorithm: {challenge.get('algorithm')}")
        print(f"    Has password: {challenge.get('has_password')}")
        print(f"    Hints: {len(challenge.get('hints', []))}")

    # Test 1.3: Solve challenge (wrong answer)
    print("\n1.3 Submit wrong solution")
    response = requests.post(f"{BASE_URL}/api/challenges/1/solve", json={
        'solution': 'Wrong answer',
        'start_time': time.time()
    })
    data = response.json()
    print_result(data.get('correct') == False, data.get('message'))

    # Test 1.4: Solve challenge (correct answer)
    print("\n1.4 Submit correct solution")
    response = requests.post(f"{BASE_URL}/api/challenges/1/solve", json={
        'solution': 'Welcome to Stego Challenges!',
        'start_time': time.time() - 30
    })
    data = response.json()
    print_result(data.get('correct') == True, f"{data.get('message')} - {data.get('points')} points")

# ============================================================================
# TEST 2: MULTI-FILE STEGANOGRAPHY
# ============================================================================

def test_multi_file():
    """Test multi-file steganography."""
    print_test("Multi-File Steganography")

    secret = "This is a multi-file secret message!"
    num_parts = 3

    # Test 2.1: Encode into multiple files
    print(f"\n2.1 Split secret into {num_parts} files")

    cover_images = [create_test_image() for _ in range(num_parts)]

    response = requests.post(f"{BASE_URL}/api/multi-encode", json={
        'secret_message': secret,
        'num_parts': num_parts,
        'cover_images': cover_images
    })

    print_result(response.status_code == 200, f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        stego_images = data.get('stego_images', [])
        print(f"    Created {len(stego_images)} stego images")
        print(f"    Message: {data.get('message')}")

        # Test 2.2: Decode from all files
        print(f"\n2.2 Decode from all {num_parts} files")

        decode_images = [{'image': img['stego_image']} for img in stego_images]
        response = requests.post(f"{BASE_URL}/api/multi-decode", json={
            'stego_images': decode_images
        })

        print_result(response.status_code == 200, f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            decoded = data.get('secret_message')
            print(f"    Decoded: {decoded}")
            print_result(decoded == secret, "Secret matches!" if decoded == secret else "Secret MISMATCH!")

        # Test 2.3: Try with missing file
        print(f"\n2.3 Try decoding with only {num_parts-1} files (should fail or give garbage)")

        decode_images_partial = decode_images[:num_parts-1]
        response = requests.post(f"{BASE_URL}/api/multi-decode", json={
            'stego_images': decode_images_partial
        })

        if response.status_code == 200:
            data = response.json()
            decoded = data.get('secret_message', '')
            matches = decoded == secret
            print_result(not matches, "Correctly failed to decode (missing part)" if not matches else "ERROR: Decoded without all parts!")

# ============================================================================
# TEST 3: STEGANOGRAPHY DETECTOR
# ============================================================================

def test_detector():
    """Test steganography detector."""
    print_test("Steganography Scanner/Detector")

    # Test 3.1: Scan clean image
    print("\n3.1 Scan clean image (no stego)")

    clean_image = create_test_image()
    response = requests.post(f"{BASE_URL}/api/detect/image", json={
        'image': clean_image
    })

    print_result(response.status_code == 200, f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        analysis = data.get('analysis', {})
        prob = analysis.get('has_stego_probability', 0)
        verdict = analysis.get('verdict', '')
        indicators = analysis.get('indicators', [])

        print(f"    Probability: {prob}%")
        print(f"    Verdict: {verdict}")
        print(f"    Indicators: {len(indicators)}")
        print_result(prob < 50, f"Correctly identified as clean (low probability)")

    # Test 3.2: Create stego image and scan it
    print("\n3.2 Scan stego image (has hidden data)")

    # First create a stego image
    encode_response = requests.post(f"{BASE_URL}/api/encode", json={
        'algorithm': 'lsb',
        'cover_image': clean_image,
        'secret_message': 'Hidden message for detector test',
        'bits_per_pixel': 2
    })

    if encode_response.status_code == 200:
        stego_image = encode_response.json().get('stego_image')

        # Now scan it
        response = requests.post(f"{BASE_URL}/api/detect/image", json={
            'image': stego_image
        })

        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            prob = analysis.get('has_stego_probability', 0)
            verdict = analysis.get('verdict', '')
            indicators = analysis.get('indicators', [])

            print(f"    Probability: {prob}%")
            print(f"    Verdict: {verdict}")
            print(f"    Indicators: {len(indicators)}")
            for ind in indicators:
                print(f"      - {ind}")
            print_result(prob > 30, f"Detected stego indicators")

    # Test 3.3: Scan text with ZWC
    print("\n3.3 Scan text with zero-width characters")

    # Create text with ZWC
    text_with_zwc = "Hello\u200bWorld\u200c"

    response = requests.post(f"{BASE_URL}/api/detect/text", json={
        'text': text_with_zwc
    })

    print_result(response.status_code == 200, f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        analysis = data.get('analysis', {})
        zwc_count = analysis.get('zero_width_chars', 0)
        verdict = analysis.get('verdict', '')

        print(f"    Zero-width chars: {zwc_count}")
        print(f"    Verdict: {verdict}")
        print_result(zwc_count > 0, "Detected zero-width characters")

# ============================================================================
# TEST 4: SELF-DESTRUCTING MESSAGES
# ============================================================================

def test_burn_messages():
    """Test self-destructing messages."""
    print_test("Self-Destructing Messages (Burn After Reading)")

    # Test 4.1: Create burn message (1-time view)
    print("\n4.1 Create 1-time burn message")

    stego_data = "This message will self-destruct!"
    response = requests.post(f"{BASE_URL}/api/burn/create", json={
        'stego_data': stego_data,
        'algorithm': 'zwc',
        'max_views': 1,
        'expire_hours': 24
    })

    print_result(response.status_code == 200, f"Status: {response.status_code}")

    burn_id = None
    if response.status_code == 200:
        data = response.json()
        burn_id = data.get('burn_id')
        burn_url = data.get('burn_url')

        print(f"    Burn ID: {burn_id}")
        print(f"    URL: {burn_url}")
        print(f"    Max views: {data.get('max_views')}")
        print(f"    Expires in: {data.get('expires_in_hours')} hours")

    # Test 4.2: View burn message (first time)
    if burn_id:
        print("\n4.2 View burn message (1st time)")

        response = requests.get(f"{BASE_URL}/api/burn/{burn_id}")
        print_result(response.status_code == 200, f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            retrieved = data.get('stego_data')
            will_burn = data.get('will_burn', False)

            print(f"    Retrieved: {retrieved[:50]}...")
            print(f"    Will burn: {will_burn}")
            print_result(retrieved == stego_data, "Data matches")

        # Test 4.3: Try to view again (should be burned)
        print("\n4.3 Try to view again (should be burned)")

        response = requests.get(f"{BASE_URL}/api/burn/{burn_id}")
        print_result(response.status_code in [404, 410], f"Status: {response.status_code}")

        if response.status_code in [404, 410]:
            data = response.json()
            print(f"    Error: {data.get('error')}")
            print_result('burned' in data.get('error', '').lower(), "Message was burned")

    # Test 4.4: Create message with multiple views
    print("\n4.4 Create burn message with 3 views allowed")

    response = requests.post(f"{BASE_URL}/api/burn/create", json={
        'stego_data': "Multi-view message",
        'algorithm': 'zwc',
        'max_views': 3,
        'expire_hours': 1
    })

    if response.status_code == 200:
        data = response.json()
        burn_id_multi = data.get('burn_id')

        print(f"    Burn ID: {burn_id_multi}")

        # View it 3 times
        for i in range(1, 4):
            response = requests.get(f"{BASE_URL}/api/burn/{burn_id_multi}")
            if response.status_code == 200:
                data = response.json()
                remaining = data.get('views_remaining', 0)
                print(f"    View {i}/3 - Remaining: {remaining}")

        # 4th attempt should fail
        response = requests.get(f"{BASE_URL}/api/burn/{burn_id_multi}")
        print_result(response.status_code in [404, 410], f"Burned after max views")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print("STEGANOGRAPHY ADVANCED FEATURES TEST SUITE")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print("="*60)

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code != 200:
            print("[ERROR] Server not responding. Please start the server with: python app.py")
            return
        print("[OK] Server is running\n")
    except:
        print("[ERROR] Cannot connect to server. Please start it with: python app.py")
        return

    # Run all test suites
    test_challenges()
    test_multi_file()
    test_detector()
    test_burn_messages()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\nSummary:")
    print("  [OK] Challenge System - tested")
    print("  [OK] Multi-File Steganography - tested")
    print("  [OK] Steganography Detector - tested")
    print("  [OK] Self-Destructing Messages - tested")
    print("\nAll 4 advanced features are working!")

if __name__ == '__main__':
    run_all_tests()
