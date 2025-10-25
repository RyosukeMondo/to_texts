#!/bin/bash
# Wrapper script to search 2025 books, download all results, and save to database
# Usage: ./scripts/run_2025_all_pages_dl_all_db.sh --title "Your Search Query"

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

# Extract title from arguments
TITLE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --title)
            TITLE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --title \"Your Search Query\""
            exit 1
            ;;
    esac
done

# Check if title was provided
if [ -z "$TITLE" ]; then
    echo "Error: --title is required"
    echo "Usage: $0 --title \"Your Search Query\""
    exit 1
fi

echo "=========================================="
echo "Z-Library 2025 Books Downloader"
echo "=========================================="
echo "Search query: $TITLE"
echo "Year: 2025"
echo "Mode: Download ALL results + Save to DB"
echo "=========================================="
echo ""

# Run the Python module with all arguments hardcoded except title
python -m zlibrary_downloader.cli \
    --title "$TITLE" \
    --year-from 2025 \
    --year-to 2025 \
    --all-pages \
    --download-all \
    --save-db
