#!/bin/bash

echo "Starting Regulatory Compliance Engine Frontend..."
echo

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ and try again"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH"
    echo "Please install npm and try again"
    exit 1
fi

# Navigate to frontend directory
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
else
    echo "Dependencies already installed, checking for updates..."
    npm install
fi

# Start the development server
echo
echo "Starting Vite development server on http://localhost:5173"
echo "Press Ctrl+C to stop the server"
echo
npm run dev
