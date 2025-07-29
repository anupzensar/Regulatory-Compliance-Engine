#!/bin/bash

echo "Starting Both Backend and Frontend Services..."
echo

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup background processes
cleanup() {
    echo
    echo "Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "Starting backend server..."
"$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!

# Wait a few seconds for backend to start
sleep 5

# Start frontend in background
echo "Starting frontend server..."
"$SCRIPT_DIR/start-frontend.sh" &
FRONTEND_PID=$!

echo
echo "Both services are running:"
echo "- Backend: http://localhost:7000"
echo "- Frontend: http://localhost:5173"
echo "- API Docs: http://localhost:7000/docs"
echo
echo "Press Ctrl+C to stop both services..."

# Wait for either process to finish
wait
