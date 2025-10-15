#!/bin/bash
# download_and_extract.sh
# Download books from Z-Library and extract text in one command

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/packages/python/zlibrary-downloader"
RUST_DIR="$SCRIPT_DIR/packages/rust"
DOWNLOADS_DIR="$PYTHON_DIR/downloads"

# Usage function
usage() {
    echo "Usage: $0 <book_title> [output_dir] [options]"
    echo ""
    echo "Arguments:"
    echo "  book_title          Book title to search for (required)"
    echo "  output_dir          Directory for extracted .txt files (default: ./extracted_texts/)"
    echo ""
    echo "Options:"
    echo "  --format FORMAT     File format (pdf, epub, mobi, etc.) - default: epub"
    echo "  --year-from YEAR    Filter books published from this year"
    echo "  --year-to YEAR      Filter books published until this year"
    echo "  --year YEAR         Filter books published in specific year (shorthand for --year-from YEAR --year-to YEAR)"
    echo "  --language LANG     Filter by language (english, spanish, etc.)"
    echo "  --delete-original   Delete the downloaded EPUB/PDF file after extraction (default: keep)"
    echo "  --limit N           Maximum number of search results (default: 1)"
    echo ""
    echo "Examples:"
    echo "  # Download a specific book"
    echo "  $0 \"Atomic Habits\""
    echo ""
    echo "  # Download 2024 books"
    echo "  $0 \"The Anxious Generation\" --year 2024"
    echo "  $0 \"psychology\" --year-from 2024 --limit 3"
    echo ""
    echo "  # Download books from a year range"
    echo "  $0 \"Machine Learning\" --year-from 2020 --year-to 2024 --limit 5"
    echo ""
    echo "  # Advanced search"
    echo "  $0 \"Python Programming\" ./texts/ --format pdf --year-from 2023 --language english"
    echo ""
    exit 1
}

# Check for help flag first
if [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]; then
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Book title is required${NC}"
        echo ""
    fi
    usage
fi

BOOK_TITLE="$1"
shift

# Default values
OUTPUT_DIR="$SCRIPT_DIR/extracted_texts"
FORMAT="epub"
KEEP_ORIGINAL=true
YEAR_FROM=""
YEAR_TO=""
LANGUAGE=""
LIMIT=""

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --year-from)
            YEAR_FROM="$2"
            shift 2
            ;;
        --year-to)
            YEAR_TO="$2"
            shift 2
            ;;
        --year)
            YEAR_FROM="$2"
            YEAR_TO="$2"
            shift 2
            ;;
        --language)
            LANGUAGE="$2"
            shift 2
            ;;
        --delete-original)
            KEEP_ORIGINAL=false
            shift
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            # If it doesn't start with --, treat it as output directory
            if [[ ! "$1" =~ ^-- ]]; then
                OUTPUT_DIR="$1"
            fi
            shift
            ;;
    esac
done

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Download & Extract Text${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "Book: ${GREEN}$BOOK_TITLE${NC}"
echo -e "Format: ${GREEN}$FORMAT${NC}"
if [ -n "$YEAR_FROM" ] && [ -n "$YEAR_TO" ]; then
    if [ "$YEAR_FROM" = "$YEAR_TO" ]; then
        echo -e "Year: ${GREEN}$YEAR_FROM${NC}"
    else
        echo -e "Year Range: ${GREEN}$YEAR_FROM - $YEAR_TO${NC}"
    fi
elif [ -n "$YEAR_FROM" ]; then
    echo -e "Year From: ${GREEN}$YEAR_FROM${NC}"
elif [ -n "$YEAR_TO" ]; then
    echo -e "Year To: ${GREEN}$YEAR_TO${NC}"
fi
if [ -n "$LANGUAGE" ]; then
    echo -e "Language: ${GREEN}$LANGUAGE${NC}"
fi
if [ -n "$LIMIT" ]; then
    echo -e "Limit: ${GREEN}$LIMIT results${NC}"
fi
echo -e "Output: ${GREEN}$OUTPUT_DIR${NC}"
echo ""

# Step 1: Download the book
echo -e "${YELLOW}[1/3] Downloading from Z-Library...${NC}"
cd "$PYTHON_DIR"

# Build the download command
DOWNLOAD_CMD="source venv/bin/activate && python -m zlibrary_downloader.cli --title \"$BOOK_TITLE\" --download --format $FORMAT"

# Add optional filters
if [ -n "$YEAR_FROM" ]; then
    DOWNLOAD_CMD="$DOWNLOAD_CMD --year-from $YEAR_FROM"
fi

if [ -n "$YEAR_TO" ]; then
    DOWNLOAD_CMD="$DOWNLOAD_CMD --year-to $YEAR_TO"
fi

if [ -n "$LANGUAGE" ]; then
    DOWNLOAD_CMD="$DOWNLOAD_CMD --language $LANGUAGE"
fi

if [ -n "$LIMIT" ]; then
    DOWNLOAD_CMD="$DOWNLOAD_CMD --limit $LIMIT"
fi

# Execute download
if ! eval "$DOWNLOAD_CMD"; then
    echo -e "${RED}Error: Download failed${NC}"
    exit 1
fi

echo ""

# Step 2: Extract text using Rust CLI
echo -e "${YELLOW}[2/3] Extracting text...${NC}"
cd "$RUST_DIR"

if ! ./target/release/text-extractor --target "$DOWNLOADS_DIR" --output "$OUTPUT_DIR"; then
    echo -e "${RED}Error: Text extraction failed${NC}"
    exit 1
fi

echo ""

# Step 3: Cleanup (optional)
if [ "$KEEP_ORIGINAL" = false ]; then
    echo -e "${YELLOW}[3/3] Cleaning up original files...${NC}"
    # Remove the downloaded EPUB/PDF files, keep only .txt
    find "$DOWNLOADS_DIR" -type f \( -name "*.epub" -o -name "*.pdf" -o -name "*.mobi" \) -delete
    echo -e "${GREEN}Original files removed${NC}"
else
    echo -e "${YELLOW}[3/3] Keeping original files in: $DOWNLOADS_DIR${NC}"
fi

echo ""
echo -e "${GREEN}✓ Complete!${NC}"
echo -e "Extracted text files are in: ${BLUE}$OUTPUT_DIR${NC}"
echo ""

# Show the extracted files
echo -e "${BLUE}Extracted files:${NC}"
ls -lh "$OUTPUT_DIR"/*.txt 2>/dev/null || echo "No .txt files found"
