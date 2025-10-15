#!/bin/bash
# Run script for Z-Library downloader

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Run the module as a script
python -m zlibrary_downloader.cli "$@"
