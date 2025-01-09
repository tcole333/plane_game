#!/bin/bash

# Start the backend server
cd backend
python3 game_server.py &

# Start the radar display
python3 radar_display.py &

# Build and serve the frontend
cd ../frontend
npm run build
npx serve dist

echo "All services started!"