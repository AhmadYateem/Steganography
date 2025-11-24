import sys
import os

# Add your project directory to the sys.path
# CHANGE 'yourusername' to your actual PythonAnywhere username
project_home = '/home/yourusername'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import Flask app
from app import app as application

# This is what PythonAnywhere will use to run your app
