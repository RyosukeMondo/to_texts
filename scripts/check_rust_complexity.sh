#!/bin/bash
set -e

# Rust Complexity Checker Script
# Runs rust-code-analysis-cli on Rust source files and validates cyclomatic complexity ≤10
# Usage: ./scripts/check_rust_complexity.sh

# Get script directory for reliable path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Define paths
RUST_SRC_PATH="$PROJECT_ROOT/packages/rust/text-extractor/src"
TEMP_METRICS_FILE="/tmp/rust_metrics_$$.json"
PARSER_SCRIPT="$SCRIPT_DIR/parse_rust_complexity.py"
COMPLEXITY_THRESHOLD=10

# Cleanup function
cleanup() {
    rm -f "$TEMP_METRICS_FILE"
}
trap cleanup EXIT

# Check if rust-code-analysis-cli is installed
if ! command -v rust-code-analysis-cli &> /dev/null; then
    echo "Error: rust-code-analysis-cli is not installed."
    echo "Install with: cargo install rust-code-analysis-cli"
    exit 2
fi

# Check if Rust source directory exists
if [ ! -d "$RUST_SRC_PATH" ]; then
    echo "Error: Rust source directory not found: $RUST_SRC_PATH"
    exit 2
fi

# Check if parser script exists
if [ ! -f "$PARSER_SCRIPT" ]; then
    echo "Error: Parser script not found: $PARSER_SCRIPT"
    exit 2
fi

# Run rust-code-analysis-cli and save JSON output
echo "Running Rust complexity analysis..."
if ! rust-code-analysis-cli --metrics -O json -p "$RUST_SRC_PATH" > "$TEMP_METRICS_FILE" 2>&1; then
    echo "Error: rust-code-analysis-cli failed"
    exit 2
fi

# Parse JSON output and check for complexity violations
python3 "$PARSER_SCRIPT" "$TEMP_METRICS_FILE" "$COMPLEXITY_THRESHOLD"
