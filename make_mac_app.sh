#!/bin/bash
set -e  # Exit on error

echo "=== GIF Framing Tool Build Script ==="
echo "Building macOS application..."

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Ensure all dependencies are installed
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Check for logo.png
if [ ! -f "logo.png" ]; then
    echo "Warning: logo.png not found in the current directory."
    echo "The application will be built without a custom icon."
fi

# Check for frame.png
if [ ! -f "frame.png" ]; then
    echo "Warning: frame.png not found in the current directory."
    echo "The application will need a frame image to be selected manually."
fi

# Run the build script
echo "Running build script..."
python3 build_app.py

# Open the dist folder if build was successful
if [ -d "dist" ]; then
    echo "Opening dist folder..."
    open dist
    
    echo "=== Build Complete ==="
    echo "Your application is ready in the dist folder."
    echo "You can now drag 'GIF Framing Tool.app' to your Applications folder."
else
    echo "=== Build Failed ==="
    echo "Check the output above for errors."
    exit 1
fi
