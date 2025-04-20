#!/bin/bash
# Script to help with Docker operations for PaperShelf

# Set the directory to the script's directory
cd "$(dirname "$0")/.." || exit

# Function to display help
show_help() {
    echo "PaperShelf Docker Helper Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  dev             Start the development environment"
    echo "  dev-build       Build and start the development environment"
    echo "  prod            Start the production environment"
    echo "  prod-build      Build and start the production environment"
    echo "  stop            Stop the running containers"
    echo "  logs            View logs from the containers"
    echo "  clean           Remove all containers and volumes"
    echo "  help            Show this help message"
    echo ""
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Process commands
case "$1" in
    dev)
        echo "Starting development environment..."
        docker-compose up
        ;;
    dev-build)
        echo "Building and starting development environment..."
        docker-compose up --build
        ;;
    prod)
        echo "Starting production environment..."
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    prod-build)
        echo "Building and starting production environment..."
        docker-compose -f docker-compose.prod.yml up --build -d
        ;;
    stop)
        echo "Stopping containers..."
        docker-compose down
        docker-compose -f docker-compose.prod.yml down
        ;;
    logs)
        if [ "$2" == "prod" ]; then
            echo "Viewing production logs..."
            docker-compose -f docker-compose.prod.yml logs -f
        else
            echo "Viewing development logs..."
            docker-compose logs -f
        fi
        ;;
    clean)
        echo "Removing all containers and volumes..."
        docker-compose down -v
        docker-compose -f docker-compose.prod.yml down -v
        ;;
    help|*)
        show_help
        ;;
esac