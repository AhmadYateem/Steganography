"""
Test script for the Steganography API

This script validates the API structure without needing to run the Flask server.
It checks that all modules are properly organized and importable.

To run full API tests, first install Flask:
    pip install Flask>=3.0.0

Then run the server and use the examples in API_GUIDE.md
"""

import sys


def test_module_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        import text_stego
        print("✓ text_stego module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import text_stego: {e}")
        return False

    try:
        import image_stego
        print("✓ image_stego module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import image_stego: {e}")
        return False

    try:
        import security
        print("✓ security module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import security: {e}")
        return False

    try:
        import metrics
        print("✓ metrics module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import metrics: {e}")
        return False

    return True


def test_text_steganography():
    """Test basic text steganography functions."""
    print("\nTesting text steganography...")

    import text_stego

    # Test encoding
    cover = "Hello world"
    secret = "Secret!"

    stego = text_stego.encode_message(cover, secret, encoding_bits=2)
    print(f"✓ Encoded message into text (length: {len(stego)})")

    # Test decoding
    decoded = text_stego.decode_message(stego, encoding_bits=2)

    if decoded == secret:
        print(f"✓ Decoded message correctly: '{decoded}'")
        return True
    else:
        print(f"✗ Decoding failed. Expected '{secret}', got '{decoded}'")
        return False


def test_security():
    """Test encryption/decryption."""
    print("\nTesting security module...")

    import security

    message = "Test message"
    password = "testpass"

    # Encrypt
    encrypted = security.encrypt_message(message, password)
    print(f"✓ Encrypted message (length: {len(encrypted)})")

    # Decrypt
    decrypted = security.decrypt_message(encrypted, password)

    if decrypted == message:
        print(f"✓ Decrypted message correctly: '{decrypted}'")
        return True
    else:
        print(f"✗ Decryption failed. Expected '{message}', got '{decrypted}'")
        return False


def test_api_structure():
    """Test that app.py has the correct structure."""
    print("\nTesting API structure...")

    try:
        # Check if Flask is available
        import flask
        flask_installed = True
    except ImportError:
        print("⚠️  Flask not installed - skipping API server tests")
        print("   To install: pip install Flask>=3.0.0")
        flask_installed = False

    # Check if app.py exists
    import os
    if not os.path.exists('app.py'):
        print("✗ app.py not found")
        return False

    print("✓ app.py exists")

    if flask_installed:
        # Try importing the app
        try:
            import app
            print("✓ app module imported successfully")

            # Check routes
            if hasattr(app, 'app'):
                flask_app = app.app
                print(f"✓ Flask app found with {len(flask_app.url_map._rules)} routes")

                # List routes
                print("\nAvailable routes:")
                for rule in flask_app.url_map.iter_rules():
                    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"  {methods:6s} {rule.rule}")

                return True
            else:
                print("✗ Flask app object not found in app.py")
                return False

        except Exception as e:
            print(f"✗ Failed to import app: {e}")
            return False
    else:
        print("⚠️  Skipping Flask app validation (Flask not installed)")
        return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("  STEGANOGRAPHY API VALIDATION TESTS")
    print("=" * 70)

    tests = [
        ("Module Imports", test_module_imports),
        ("Text Steganography", test_text_steganography),
        ("Security", test_security),
        ("API Structure", test_api_structure),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {name}")

    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n✓ All tests passed! API is ready to use.")
        print("\nTo start the server:")
        print("  1. pip install Flask>=3.0.0")
        print("  2. python app.py")
        print("  3. Visit http://localhost:5000/ping")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
