#!/bin/bash

# Script to run the Smart Expense Intelligence System

echo "Starting Smart Expense Intelligence System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.template .env
    echo "Please edit .env and add your Baidu AI Studio API credentials"
fi

# Start backend
echo "Starting backend server..."
python backend/app.py &

# Wait a moment for backend to start
sleep 3

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev

echo "System started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

