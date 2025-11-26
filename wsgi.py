import sys
import os

# Add your project directory to the sys.path
# CHANGE 'yourusername' to your actual PythonAnywhere username
# Example: project_home = '/home/AhmadYateem/Steganography'
project_home = os.path.dirname(os.path.abspath(__file__))

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')

# Import Flask app
try:
    from app import app as application
    print(f"✅ Application loaded successfully from {project_home}")
except Exception as e:
    print(f"❌ Failed to load application: {e}")
    raise

# This is what PythonAnywhere will use to run your app
