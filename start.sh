#!/bin/bash

# Steganography Suite - Quick Start Script
# This script makes it easy to start the application

echo "======================================================================"
echo "  🎨 Steganography Suite - Apple-Level Professional Interface"
echo "======================================================================"
echo ""

# Check if Flask-CORS is installed
if ! python -c "import flask_cors" 2>/dev/null; then
    echo "⚠️  Flask-CORS not installed. Installing now..."
    pip install Flask-CORS>=4.0.0
    echo ""
fi

echo "✨ Starting Steganography Suite..."
echo ""
echo "📍 Server will run on: http://localhost:5000"
echo "🌐 Open this URL in your browser to see the beautiful interface!"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo ""
echo "======================================================================"
echo ""

# Start Flask server
python app.py
