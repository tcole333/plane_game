#!/bin/bash

# Ensure you're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your virtual environment first with:"
    echo "source venv/bin/activate"
    exit 1
fi

# Install backend dependencies
cd backend
pip3 install -r requirements.txt

# Install frontend dependencies (requires Node.js)
cd ../frontend
npm install

echo "Installation complete!"