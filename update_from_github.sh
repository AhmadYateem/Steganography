#!/bin/bash

# Quick Update Script for PythonAnywhere
# Run this after pushing changes to GitHub

echo "====================================="
echo "Pulling latest changes from GitHub..."
echo "====================================="

cd ~/steganography-app  # Change if your repo name is different
git pull origin main

echo ""
echo "====================================="
echo "Changes pulled successfully!"
echo "====================================="
echo ""
echo "Don't forget to:"
echo "1. Go to the Web tab in PythonAnywhere"
echo "2. Click the green 'Reload' button"
echo ""
echo "Your app will be updated in 5-10 seconds!"
echo "====================================="
