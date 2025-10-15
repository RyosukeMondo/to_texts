#!/bin/bash
# Setup script for Z-Library downloader

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/../../.." && pwd)"

cd "$PROJECT_DIR"

echo "Z-Library Downloader Setup"
echo "=========================="

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists at ./venv"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created at ./venv"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in editable mode
echo "Installing package in editable mode..."
pip install -e .

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env at the root and add your credentials:"
echo "   cp $ROOT_DIR/.env.example $ROOT_DIR/.env"
echo "2. Edit .env with your Z-Library credentials"
echo "3. Run the downloader with: ./scripts/run.sh --title \"book title\""
