#!/bin/bash
# Start script for Daxco POC application without Docker

# Start the backend
echo "Starting backend server..."
cd "$(dirname "$0")/backend"
source venv/bin/activate
# Try port 5000 first, then try 5001 if 5000 is in use
if nc -z 0.0.0.0 5000 > /dev/null 2>&1; then
  echo "Port 5000 is already in use, trying port 5001 instead..."
  uvicorn main:app --host 0.0.0.0 --port 5001 &
else
  uvicorn main:app --host 0.0.0.0 --port 5000 &
fi
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the frontend
echo "Starting frontend server..."
# Debug: Print current directory
# cd "$(dirname "$0")"  # Return to project root
# pwd
# echo "Listing directory content:"
# ls -la
cd ../react-mui-csv-app  # Navigate to the React app directory
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit 0
}

# Register the cleanup function for SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Servers started. Press Ctrl+C to stop."
wait
