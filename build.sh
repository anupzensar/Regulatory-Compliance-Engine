#!/bin/bash

echo "Building Regulatory Compliance Engine for Production..."
echo

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Build Backend
echo "Building backend..."
cd "$SCRIPT_DIR/backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Warning: No virtual environment found"
fi

echo "Backend is ready for production deployment"
echo

# Build Frontend
echo "Building frontend..."
cd "$SCRIPT_DIR/frontend"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Build the frontend
echo "Creating production build..."
npm run build
if [ $? -ne 0 ]; then
    echo "Error: Failed to build frontend"
    exit 1
fi

echo
echo "Build completed successfully!"
echo "- Frontend build is in: frontend/dist/"
echo "- Backend is ready for production deployment"
echo
echo "To preview the production build, run: npm run preview (from frontend directory)"
echo
