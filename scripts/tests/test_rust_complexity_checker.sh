#!/bin/bash

# Test script for check_rust_complexity.sh
# Tests the basic functionality and error handling of the Rust complexity checker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER_SCRIPT="$SCRIPT_DIR/../check_rust_complexity.sh"

echo "Testing check_rust_complexity.sh..."

# Test 1: Verify script exists and is executable
echo "Test 1: Script exists and is executable"
if [ ! -f "$CHECKER_SCRIPT" ]; then
    echo "FAIL: Script not found at $CHECKER_SCRIPT"
    exit 1
fi

if [ ! -x "$CHECKER_SCRIPT" ]; then
    echo "FAIL: Script is not executable"
    exit 1
fi
echo "PASS: Script exists and is executable"

# Test 2: Verify script has proper shebang
echo "Test 2: Script has proper shebang"
FIRST_LINE=$(head -n 1 "$CHECKER_SCRIPT")
if [ "$FIRST_LINE" != "#!/bin/bash" ]; then
    echo "FAIL: Script does not have #!/bin/bash shebang, found: $FIRST_LINE"
    exit 1
fi
echo "PASS: Script has proper shebang"

# Test 3: Verify script uses 'set -e'
echo "Test 3: Script uses 'set -e' for error propagation"
if ! grep -q "^set -e" "$CHECKER_SCRIPT"; then
    echo "FAIL: Script does not use 'set -e'"
    exit 1
fi
echo "PASS: Script uses 'set -e'"

# Test 4: Verify script checks for rust-code-analysis-cli
echo "Test 4: Script checks for rust-code-analysis-cli installation"
if ! grep -q "rust-code-analysis-cli" "$CHECKER_SCRIPT"; then
    echo "FAIL: Script does not check for rust-code-analysis-cli"
    exit 1
fi
echo "PASS: Script references rust-code-analysis-cli"

# Test 5: Verify script calls parser script
echo "Test 5: Script calls parser script"
if ! grep -q "parse_rust_complexity.py" "$CHECKER_SCRIPT"; then
    echo "FAIL: Script does not call parse_rust_complexity.py"
    exit 1
fi
echo "PASS: Script calls parser script"

# Test 6: Verify script uses proper path resolution
echo "Test 6: Script uses proper path resolution"
if ! grep -q "SCRIPT_DIR" "$CHECKER_SCRIPT"; then
    echo "FAIL: Script does not use script directory resolution"
    exit 1
fi
echo "PASS: Script uses proper path resolution"

# Test 7: Verify script has cleanup trap
echo "Test 7: Script has cleanup trap"
if ! grep -q "trap cleanup EXIT" "$CHECKER_SCRIPT"; then
    echo "FAIL: Script does not have cleanup trap"
    exit 1
fi
echo "PASS: Script has cleanup trap"

echo ""
echo "All tests passed!"
