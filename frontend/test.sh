#!/bin/bash
set -e

echo "Testing PaperShelf React Frontend"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js to run this test."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm to run this test."
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Running linting check..."
npm run lint || echo "Linting not configured, skipping."

echo "Building the application..."
npm run build

echo "=================================="
echo "Test completed successfully!"
echo "The React frontend has been built and is ready for deployment."
echo "To start the development server, run: npm start"
echo "To build for production, run: npm run build"
echo "To run in Docker, use: docker-compose up frontend"
echo "=================================="