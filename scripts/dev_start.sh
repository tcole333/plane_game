#!/bin/bash

# Ensure virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your virtual environment first with:"
    echo "source venv/bin/activate"
    exit 1
fi

# Start the backend server
cd backend
python3 game_server.py &
SERVER_PID=$!

# Start the radar display in a new terminal
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && source ../venv/bin/activate && python3 radar_display.py"'

# Start the frontend development server
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Development servers started!"
echo "Frontend running at http://localhost:5173"
echo "Backend running at http://localhost:8000"
echo ""
echo "To stop all servers, press Ctrl+C"

# Wait for Ctrl+C
trap "kill $SERVER_PID $FRONTEND_PID" INT
wait