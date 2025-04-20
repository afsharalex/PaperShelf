#!/bin/bash
# Script to run tests with coverage reporting

# Set the directory to the script's directory
cd "$(dirname "$0")/.." || exit

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first."
    exit 1
fi

# Parse arguments
COVERAGE=0
HTML_REPORT=0
VERBOSE=0
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=1
            shift
            ;;
        --html|-h)
            HTML_REPORT=1
            COVERAGE=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--coverage|-c] [--html|-h] [--verbose|-v] [--test|-t TEST_PATH]"
            exit 1
            ;;
    esac
done

# Build the command
CMD="poetry run pytest"

if [ $VERBOSE -eq 1 ]; then
    CMD="$CMD -v"
fi

if [ $COVERAGE -eq 1 ]; then
    CMD="$CMD --cov=papershelf"
    
    if [ $HTML_REPORT -eq 1 ]; then
        CMD="$CMD --cov-report=html"
    fi
fi

# shellcheck disable=SC2236
if [ ! -z "$SPECIFIC_TEST" ]; then
    CMD="$CMD $SPECIFIC_TEST"
fi

# Run the command
echo "Running: $CMD"
$CMD

# If HTML report was generated, print the path
if [ $HTML_REPORT -eq 1 ]; then
    echo ""
    echo "HTML coverage report generated in: $(pwd)/htmlcov/index.html"
    
    # Try to open the report in the default browser
    if command -v open &> /dev/null; then
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    elif command -v start &> /dev/null; then
        start htmlcov/index.html
    else
        echo "Please open the report manually in your browser."
    fi
fi