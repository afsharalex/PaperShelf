#!/bin/bash
# Script to run the PaperShelf application in development mode

# Set the directory to the script's directory
cd "$(dirname "$0")/.."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env file from .env.example. Please edit it with your settings."
    else
        echo "Error: .env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Parse arguments
HOST="0.0.0.0"
PORT="8000"
RELOAD=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --host|-h)
            HOST="$2"
            shift 2
            ;;
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --reload|-r)
            RELOAD=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--host|-h HOST] [--port|-p PORT] [--reload|-r]"
            exit 1
            ;;
    esac
done

# Build the command
CMD="poetry run uvicorn papershelf.api.app:app --host $HOST --port $PORT"

if [ $RELOAD -eq 1 ]; then
    CMD="$CMD --reload"
fi

# Run the command
echo "Starting PaperShelf development server..."
echo "Running: $CMD"
$CMD