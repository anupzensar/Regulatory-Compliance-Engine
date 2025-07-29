#!/bin/bash

echo "Setting up Regulatory Compliance Engine..."
echo

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make all shell scripts executable
echo "Making shell scripts executable..."
chmod +x "$SCRIPT_DIR/start-backend.sh"
chmod +x "$SCRIPT_DIR/start-frontend.sh" 
chmod +x "$SCRIPT_DIR/start-all.sh"
chmod +x "$SCRIPT_DIR/build.sh"

echo "Setup complete!"
echo
echo "Available commands:"
echo "- ./start-backend.sh   - Start only the backend server"
echo "- ./start-frontend.sh  - Start only the frontend server"  
echo "- ./start-all.sh       - Start both backend and frontend"
echo "- ./build.sh           - Build for production"
echo
echo "You can now run any of these scripts directly."
