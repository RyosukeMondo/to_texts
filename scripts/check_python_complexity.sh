#!/bin/bash
set -e

# Check Python cyclomatic complexity using radon
# This script is called by pre-commit hooks to enforce complexity ≤10

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if radon is installed
if ! command -v radon &> /dev/null; then
    echo "Error: radon is not installed. Install it with: pip install radon>=6.0.0"
    exit 1
fi

# Find all Python files in the project (excluding venv, __pycache__, etc.)
PYTHON_FILES=$(find packages/python -type f -name "*.py" \
    -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.*" \
    -not -path "*.egg-info/*" \
    2>/dev/null || true)

if [ -z "$PYTHON_FILES" ]; then
    echo "No Python files found to check"
    exit 0
fi

# Create temporary file for JSON output
TEMP_JSON=$(mktemp)
trap "rm -f $TEMP_JSON" EXIT

# Run radon with JSON output
# --min C: Show functions with complexity C and above (moderate complexity)
# --json: Output in JSON format for parsing
radon cc --min C --json $PYTHON_FILES > "$TEMP_JSON" 2>&1 || {
    echo "Error: radon failed to run"
    cat "$TEMP_JSON"
    exit 2
}

# Call Python parser script to validate complexity threshold
python3 "$SCRIPT_DIR/parse_python_complexity.py" "$TEMP_JSON" 10
exit $?
