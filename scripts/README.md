# PaperShelf Scripts

This directory contains utility scripts for development and testing of the PaperShelf application.

## Available Scripts

### run_dev.sh

A script to run the PaperShelf application in development mode.

```bash
# Run with default settings (host: 0.0.0.0, port: 8000)
./run_dev.sh

# Run on a specific host and port
./run_dev.sh --host 127.0.0.1 --port 9000

# Run with auto-reload for development
./run_dev.sh --reload

# Combine options
./run_dev.sh --host 127.0.0.1 --port 9000 --reload
```

### run_tests.sh

A script to run tests with various options.

```bash
# Run all tests
./run_tests.sh

# Run tests with verbose output
./run_tests.sh --verbose

# Run tests with coverage reporting
./run_tests.sh --coverage

# Generate HTML coverage report
./run_tests.sh --html

# Run a specific test or test directory
./run_tests.sh --test tests/ingest/

# Combine options
./run_tests.sh --verbose --html --test tests/api/test_api.py
```

### docker.sh

A helper script for Docker operations.

```bash
# Start the development environment
./docker.sh dev

# Build and start the development environment
./docker.sh dev-build

# Start the production environment
./docker.sh prod

# Build and start the production environment
./docker.sh prod-build

# Stop the running containers
./docker.sh stop

# View logs from the development containers
./docker.sh logs

# View logs from the production containers
./docker.sh logs prod

# Remove all containers and volumes
./docker.sh clean

# Show help message
./docker.sh help
```

## Adding New Scripts

When adding new scripts to this directory:

1. Make sure the script is executable (`chmod +x script_name.sh`)
2. Add a description of the script to this README.md file
3. Include usage examples
4. Update the main README.md file if the script is intended for general use
