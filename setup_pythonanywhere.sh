#!/bin/bash

# Quick Setup Script for PythonAnywhere Deployment
# Run this in PythonAnywhere Bash console after uploading files

echo "====================================="
echo "Installing Python Dependencies..."
echo "====================================="

pip3.10 install --user flask flask-cors cryptography pillow numpy scikit-image

echo ""
echo "====================================="
echo "Installation Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Go to the 'Web' tab"
echo "2. Create a new web app (Flask, Python 3.10)"
echo "3. Configure WSGI file with wsgi.py content"
echo "4. Set static files: URL=/static/ Path=/home/yourusername/static"
echo "5. Click Reload"
echo ""
echo "Your app will be live at: yourusername.pythonanywhere.com"
echo "====================================="
