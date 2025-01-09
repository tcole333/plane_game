#!/bin/bash

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-pygame nodejs npm

# Install backend dependencies
cd backend
pip3 install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

echo "Installation complete!"