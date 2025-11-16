"""
Steganography Suite - Cross-Platform Launcher

This Python script works on Windows, Mac, and Linux.
Use this if start.sh doesn't work on your system.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required packages are installed."""
    print("🔍 Checking dependencies...\n")

    missing = []

    # Check Flask
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        missing.append("Flask")
        print("❌ Flask not installed")

    # Check Flask-CORS
    try:
        import flask_cors
        print(f"✅ Flask-CORS installed")
    except ImportError:
        missing.append("Flask-CORS")
        print("❌ Flask-CORS not installed")

    # Check cryptography
    try:
        import cryptography
        print(f"✅ cryptography installed")
    except ImportError:
        missing.append("cryptography")
        print("❌ cryptography not installed")

    # Check Pillow
    try:
        import PIL
        print(f"✅ Pillow (PIL) installed")
    except ImportError:
        missing.append("Pillow")
        print("❌ Pillow not installed")

    # Check numpy
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
    except ImportError:
        missing.append("numpy")
        print("❌ NumPy not installed")

    print()

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}\n")
        print("Installing missing packages...")
        print("=" * 70)

        # Install missing packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + missing)

        print("=" * 70)
        print("✅ All packages installed!\n")
    else:
        print("✅ All dependencies satisfied!\n")

def main():
    """Launch the Steganography Suite."""
    print("=" * 70)
    print("  🎨 Steganography Suite - Apple-Level Professional Interface")
    print("=" * 70)
    print()

    # Check dependencies
    check_dependencies()

    print("=" * 70)
    print("✨ Starting Steganography Suite...")
    print()
    print("📍 Server will run on: http://localhost:5000")
    print("🌐 Open this URL in your browser to see the beautiful interface!")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Start Flask app
    try:
        # Run app.py
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTry running manually:")
        print("  python app.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
