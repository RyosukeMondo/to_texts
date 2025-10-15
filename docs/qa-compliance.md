# QA Compliance Documentation

## Table of Contents

- [Overview](#overview)
- [Quality Standards](#quality-standards)
- [Tools and Configuration](#tools-and-configuration)
- [Pre-commit Hook Workflow](#pre-commit-hook-workflow)
- [Manual Quality Checks](#manual-quality-checks)
- [Code Metrics Thresholds](#code-metrics-thresholds)
- [Emergency Bypass Procedures](#emergency-bypass-procedures)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Development Workflow](#development-workflow)
- [CI/CD Integration](#cicd-integration)

## Overview

The to_texts monorepo implements comprehensive Quality Assurance (QA) compliance infrastructure to enforce code quality standards through automated tooling and pre-commit verification. This system ensures maintainability, reliability, and consistency across both Rust and Python codebases.

**Key Benefits:**
- Catch quality issues before commit (shift-left approach)
- Consistent code style across the project
- Reduced technical debt accumulation
- Higher confidence in code changes
- Enforced best practices via automation

**Architecture:** The QA system uses a layered approach:
1. **Git Hook Layer:** Pre-commit framework intercepts commits
2. **Validation Layer:** Individual quality tools (type checkers, linters, formatters)
3. **Configuration Layer:** Centralized tool configuration files
4. **Reporting Layer:** Clear, actionable feedback to developers

## Quality Standards

The QA compliance system enforces the following standards aligned with Product Principles defined in `product.md`:

### Code Principles (Enforced Through Automation)

- **SOLID Principles:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **SLAP (Single Level of Abstraction Principle):** Functions operate at one level of abstraction
- **SSOT (Single Source of Truth):** Avoid data duplication
- **KISS (Keep It Simple, Stupid):** Prefer simplicity over complexity

### Code Metrics & Limits

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **File Size** | ≤400 lines | Promotes modular design, easier comprehension |
| **Function Size** | ≤30 lines | Encourages focused functions, single responsibility |
| **Cyclomatic Complexity** | ≤10 | Reduces cognitive load, improves testability |
| **Line Length** | ≤100 characters | Balances readability with screen real estate |

### Type Safety

- **Rust:** Compile-time type checking via `cargo check`
- **Python:** Static type checking via `mypy` in strict mode with complete type hint coverage

### Code Quality

- **Rust:** Linting via `clippy` (all/pedantic lints), formatting via `rustfmt`
- **Python:** Linting via `flake8`, formatting via `black`

## Tools and Configuration

### Pre-commit Framework

**Tool:** `pre-commit` (≥3.0.0)

**Purpose:** Git hook management and orchestration

**Configuration File:** `.pre-commit-config.yaml` (repository root)

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

**Key Features:**
- Language-agnostic (works with Rust, Python, custom scripts)
- Built-in caching for performance
- Declarative YAML configuration
- Supports both local and remote hooks

### Rust Quality Tools

#### 1. Type Checking: `cargo check`

**Configuration:** Inherits from `Cargo.toml`

**Purpose:** Verify Rust code compiles and passes type/borrow checking

**Usage:**
```bash
cargo check --manifest-path packages/rust/Cargo.toml
```

#### 2. Linting: `cargo clippy`

**Version:** Latest stable (ships with rustup)

**Configuration File:** `packages/rust/Cargo.toml` under `[workspace.lints.clippy]`

**Configured Lints:**
- `all = "warn"` - Enable all clippy lints
- `pedantic = "warn"` - Enable pedantic lints for extra strictness
- `unwrap_used = "deny"` - Prevent `.unwrap()` in production code
- `expect_used = "deny"` - Prevent `.expect()` in production code
- `panic = "deny"` - Prevent panic macros
- `missing_docs_in_private_items = "warn"` - Encourage documentation

**Usage:**
```bash
cargo clippy --manifest-path packages/rust/Cargo.toml -- -D warnings
```

#### 3. Formatting: `rustfmt`

**Version:** Latest stable (ships with rustup)

**Configuration:** Uses rustfmt defaults (Rust style guide)

**Usage:**
```bash
# Check formatting (non-destructive)
cargo fmt --manifest-path packages/rust/Cargo.toml --check

# Auto-fix formatting
cargo fmt --manifest-path packages/rust/Cargo.toml
```

#### 4. Complexity Analysis: `rust-code-analysis-cli`

**Version:** ≥0.0.25

**Purpose:** Measure cyclomatic complexity of Rust functions

**Installation:**
```bash
cargo install rust-code-analysis-cli
```

**Usage:**
```bash
# Via pre-commit (automated)
scripts/check_rust_complexity.sh

# Manual execution
rust-code-analysis-cli --metrics -O json -p packages/rust/text-extractor/src/
```

### Python Quality Tools

#### 1. Type Checking: `mypy`

**Version:** ≥1.8.0

**Configuration File:** `packages/python/zlibrary-downloader/pyproject.toml` under `[tool.mypy]`

**Key Settings:**
- `strict = true` - Enable all optional error checking
- `disallow_untyped_defs = true` - Require type hints on all functions
- `no_implicit_optional = true` - Don't assume Optional for None defaults
- `warn_unused_ignores = true` - Warn about unnecessary `# type: ignore` comments

**Usage:**
```bash
cd packages/python/zlibrary-downloader
mypy zlibrary_downloader
```

#### 2. Linting: `flake8`

**Version:** ≥7.0.0

**Configuration File:** `.flake8` (repository root)

**Key Settings:**
- `max-line-length = 100` - Matches black configuration
- `max-complexity = 10` - McCabe complexity threshold
- `extend-ignore = E203, W503` - Black compatibility
- `per-file-ignores = __init__.py:F401` - Allow unused imports in __init__.py

**Plugins Installed:**
- `flake8-bugbear` - Additional bug detection
- `flake8-comprehensions` - Improve list/dict comprehensions
- `flake8-simplify` - Code simplification suggestions

**Usage:**
```bash
flake8 packages/python/zlibrary-downloader/zlibrary_downloader/
```

#### 3. Formatting: `black`

**Version:** ≥24.0.0

**Configuration File:** `packages/python/zlibrary-downloader/pyproject.toml` under `[tool.black]`

**Key Settings:**
- `line-length = 100` - Match project standard
- `target-version = ['py38']` - Target Python 3.8+

**Usage:**
```bash
# Check formatting (non-destructive)
black --check packages/python/zlibrary-downloader/zlibrary_downloader/

# Auto-fix formatting
black packages/python/zlibrary-downloader/zlibrary_downloader/
```

#### 4. Complexity Analysis: `radon`

**Version:** ≥6.0.0

**Purpose:** Measure cyclomatic complexity of Python functions

**Installation:**
```bash
pip install radon
```

**Usage:**
```bash
# Via pre-commit (automated)
scripts/check_python_complexity.sh

# Manual execution
radon cc --min C --json packages/python/zlibrary-downloader/zlibrary_downloader/
```

#### 5. Testing: `pytest` + `pytest-cov`

**Version:** pytest ≥8.0.0, pytest-cov ≥4.1.0

**Configuration File:** `packages/python/zlibrary-downloader/pyproject.toml` under `[tool.pytest.ini_options]`

**Key Settings:**
- `testpaths = ["tests"]` - Test discovery directory
- `--cov=zlibrary_downloader` - Measure coverage
- `--cov-report=html` - Generate HTML coverage report
- `--cov-fail-under=80` - Require ≥80% coverage

**Usage:**
```bash
cd packages/python/zlibrary-downloader
pytest
pytest --cov --cov-report=html  # With coverage report
```

### Custom Validators

#### 1. Line Count Validator

**Script:** `scripts/validate_line_count.py`

**Purpose:** Enforce 400 line limit per file

**Logic:**
- Counts non-empty, non-comment lines
- Excludes test files, generated code, build artifacts
- Applies to both `.rs` and `.py` files

**Exclusion Patterns:** `test_`, `_test.`, `target/`, `venv/`, `__pycache__`

**Usage:**
```bash
# Via pre-commit (automated)
scripts/validate_line_count.py <file1> <file2> ...

# Manual check on specific files
./scripts/validate_line_count.py packages/python/zlibrary-downloader/zlibrary_downloader/client.py
```

#### 2. Function Size Validator

**Script:** `scripts/validate_function_size.py`

**Purpose:** Enforce 30 line limit per function

**Logic:**
- Parses Python files with AST to extract function line counts
- Parses Rust files with basic regex/parsing to extract function line counts
- Counts lines excluding function signature and docstrings
- Handles both sync and async Python functions

**Usage:**
```bash
# Via pre-commit (automated)
scripts/validate_function_size.py <file1> <file2> ...

# Manual check on specific files
./scripts/validate_function_size.py packages/python/zlibrary-downloader/zlibrary_downloader/tui.py
```

#### 3. Complexity Parsers

**Scripts:**
- `scripts/parse_rust_complexity.py` - Parses rust-code-analysis JSON output
- `scripts/parse_python_complexity.py` - Parses radon JSON output

**Purpose:** Parse complexity metrics and report violations

**Exit Codes:**
- `0` - All checks passed
- `1` - Violations found
- `2` - Error (malformed JSON, missing file, etc.)

## Pre-commit Hook Workflow

### How It Works

When you attempt to commit code, the pre-commit framework automatically:

1. **Identifies changed files** based on git staging area
2. **Filters files by type** (`.rs` for Rust hooks, `.py` for Python hooks)
3. **Runs applicable hooks** in sequence:
   - Rust: cargo check → clippy → rustfmt → complexity
   - Python: mypy → flake8 → black → complexity
   - Metrics: line count → function size
4. **Reports results** for each hook (pass/fail)
5. **Blocks commit** if ANY hook fails
6. **Allows commit** only if ALL hooks pass

### Pre-commit Hook Sequence

```
Developer commits code
         ↓
    Git commit hook
         ↓
  Pre-commit Framework
         ↓
    ┌────┴────┐
    ↓         ↓
Rust Checks  Python Checks  Code Metrics
    ↓         ↓                  ↓
cargo check  mypy          Line count
    ↓         ↓                  ↓
clippy       flake8        Function size
    ↓         ↓
rustfmt      black
    ↓         ↓
complexity   complexity
    ↓         ↓
    └────┬────┘
         ↓
    All Pass?
    ┌────┴────┐
    ↓         ↓
   YES       NO
    ↓         ↓
Commit OK  Commit Blocked
           + Error Messages
```

### Example Output (Passing)

```
Rust type checking.......................................................Passed
Rust linting.............................................................Passed
Rust formatting..........................................................Passed
Rust complexity check....................................................Passed
Python type checking.....................................................Passed
Python linting...........................................................Passed
Python formatting........................................................Passed
Line count validation....................................................Passed
```

### Example Output (Failing)

```
Rust type checking.......................................................Passed
Rust linting.............................................................Failed
- hook id: cargo-clippy
- exit code: 1

error: called `.unwrap()` on an `Option` value
  --> packages/rust/text-extractor/src/main.rs:42:18
   |
42 |     let text = result.unwrap();
   |                ^^^^^^^^^^^^^^
   |
   = note: `-D clippy::unwrap-used` implied by `-D warnings`
   = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#unwrap_used

[Commit blocked until issues are fixed]
```

## Manual Quality Checks

You can run quality checks manually outside of git commits:

### Run All Pre-commit Hooks

```bash
# Check all files in repository
pre-commit run --all-files

# Check specific files
pre-commit run --files path/to/file1.py path/to/file2.rs

# Run specific hook only
pre-commit run mypy --all-files
pre-commit run cargo-clippy --all-files
```

### Rust Commands

```bash
# Type checking
cargo check --manifest-path packages/rust/Cargo.toml

# Linting
cargo clippy --manifest-path packages/rust/Cargo.toml -- -D warnings

# Formatting check
cargo fmt --manifest-path packages/rust/Cargo.toml --check

# Complexity analysis
./scripts/check_rust_complexity.sh

# Run tests
cargo test --manifest-path packages/rust/Cargo.toml
```

### Python Commands

```bash
cd packages/python/zlibrary-downloader

# Type checking
mypy zlibrary_downloader

# Linting
flake8 zlibrary_downloader

# Formatting check
black --check zlibrary_downloader

# Complexity analysis
radon cc --min C zlibrary_downloader

# Run tests
pytest

# Run tests with coverage
pytest --cov --cov-report=html
# View coverage report: open htmlcov/index.html
```

### Code Metrics Commands

```bash
# Line count validation
./scripts/validate_line_count.py packages/python/zlibrary-downloader/zlibrary_downloader/*.py

# Function size validation
./scripts/validate_function_size.py packages/python/zlibrary-downloader/zlibrary_downloader/*.py
```

## Code Metrics Thresholds

### File Size: 400 Lines

**Rationale:** Promotes modular design and easier comprehension

**Enforced By:** `scripts/validate_line_count.py`

**Counting Rules:**
- Excludes blank lines
- Excludes comment-only lines
- Excludes test files (`test_*.py`, `*_test.rs`, `tests/`)
- Excludes generated code (`target/`, `venv/`, `__pycache__`, `*.egg-info`)

**Violation Example:**
```
Line count violations:
  packages/python/zlibrary-downloader/zlibrary_downloader/client.py: 428 lines (max: 400)

Suggestion: Split this file into smaller modules (e.g., client_auth.py, client_search.py)
```

**Resolution Strategy:**
1. Identify logical boundaries in the file (e.g., authentication, search, download)
2. Extract related functions/classes into separate modules
3. Use `__init__.py` to re-export for backward compatibility

### Function Size: 30 Lines

**Rationale:** Encourages focused functions and single responsibility

**Enforced By:** `scripts/validate_function_size.py`

**Counting Rules:**
- Excludes function signature/decorator lines
- Excludes docstrings
- Includes function body only
- Applies to both Python and Rust functions

**Violation Example:**
```
Function size violations:
  packages/python/zlibrary-downloader/zlibrary_downloader/tui.py:
    get_search_params (line 47): 35 lines (max: 30)
  packages/rust/text-extractor/src/main.rs:
    extract_epub_text (line 89): 42 lines (max: 30)
```

**Resolution Strategy:**
1. Identify distinct steps within the function
2. Extract steps into helper functions with descriptive names
3. Maintain SLAP (Single Level of Abstraction Principle)
4. Ensure helper functions are cohesive and focused

### Cyclomatic Complexity: ≤10

**Rationale:** Reduces cognitive load and improves testability

**Enforced By:** `flake8` (Python), `scripts/check_rust_complexity.sh` (Rust)

**What is Cyclomatic Complexity?**
- Measures the number of linearly independent paths through code
- Calculated as: # of decision points + 1
- Decision points: `if`, `for`, `while`, `case`, `&&`, `||`, `?`, `catch`

**Complexity Guidelines:**
- **1-4:** Simple, low risk
- **5-7:** Moderate, medium risk
- **8-10:** Complex, high risk
- **>10:** Very complex, very high risk (REFACTOR REQUIRED)

**Violation Example:**
```
Python complexity check..................................................Failed
- hook id: radon-complexity
- exit code: 1

Complexity violations found:
  packages/python/zlibrary-downloader/zlibrary_downloader/tui.py:
    get_search_params (line 47): complexity 11 (max: 10)

Suggestion: Break this function into smaller helper functions
```

**Resolution Strategy:**
1. **Extract Conditional Logic:** Move complex if/else chains into separate functions
2. **Use Guard Clauses:** Early returns to reduce nesting depth
3. **Replace Nested Loops:** Extract inner loops into helper functions
4. **Use Polymorphism:** Replace conditional logic with strategy pattern (when appropriate)
5. **Simplify Boolean Expressions:** Use named variables for complex conditions

**Example Refactoring:**

**Before (Complexity: 12):**
```python
def process_data(data, options):
    if data is not None:
        if data.is_valid():
            if options.get('transform'):
                if options['transform'] == 'uppercase':
                    return data.upper()
                elif options['transform'] == 'lowercase':
                    return data.lower()
                elif options['transform'] == 'titlecase':
                    return data.title()
            elif options.get('validate'):
                if data.matches_pattern():
                    return data
        else:
            raise ValueError("Invalid data")
    return None
```

**After (Complexity: 4 + 3 + 2 = 9 across functions):**
```python
def process_data(data, options):
    if data is None:
        return None
    if not data.is_valid():
        raise ValueError("Invalid data")

    if options.get('transform'):
        return apply_transform(data, options['transform'])
    elif options.get('validate'):
        return validate_data(data)
    return None

def apply_transform(data, transform_type):
    transforms = {
        'uppercase': str.upper,
        'lowercase': str.lower,
        'titlecase': str.title,
    }
    return transforms.get(transform_type, lambda x: x)(data)

def validate_data(data):
    return data if data.matches_pattern() else None
```

### Line Length: 100 Characters

**Rationale:** Balances readability with screen real estate

**Enforced By:** `flake8` (Python), `rustfmt` (Rust defaults to 100)

**Configuration:**
- Python: `.flake8` → `max-line-length = 100`
- Python: `pyproject.toml` → `[tool.black]` → `line-length = 100`
- Rust: Uses rustfmt default

**Auto-fixing:**
```bash
# Python
black packages/python/zlibrary-downloader/zlibrary_downloader/

# Rust
cargo fmt --manifest-path packages/rust/Cargo.toml
```

## Emergency Bypass Procedures

### When to Bypass Hooks

**Acceptable Scenarios:**
- ⚠️ **Work-in-Progress (WIP) commits** on feature branches
- ⚠️ **Emergency hotfix** requiring immediate commit (rare)
- ⚠️ **Large refactoring** in progress, splitting into multiple commits

**Unacceptable Scenarios:**
- ❌ Avoiding fixing quality violations
- ❌ Merging to main/master branch
- ❌ Production deployments
- ❌ Pull request final commits

### How to Bypass

**Command:**
```bash
git commit --no-verify -m "WIP: Refactoring authentication module"
```

**Important Notes:**
- The `--no-verify` flag skips ALL pre-commit hooks
- Use sparingly and with clear justification in commit message
- Bypassed commits WILL fail CI/CD checks (if configured)
- Must fix violations before merging to main branch
- Team review required for bypassed commits

### Policy and Best Practices

1. **Document Reason:** Always explain why bypass was needed in commit message
   ```bash
   git commit --no-verify -m "WIP: Incomplete type hints migration (task 14/16)"
   ```

2. **Track Technical Debt:** Create GitHub issue to track violations needing fixes
   ```bash
   git commit --no-verify -m "Hotfix: Critical bug #123 (TODO: Fix complexity in issue #456)"
   ```

3. **Fix Before Merge:** All bypassed commits must be fixed before PR approval
   ```bash
   # Review bypassed commits before merging
   git log --all --grep="--no-verify" --oneline
   ```

4. **Team Communication:** Notify team in PR description if bypass was used
   ```markdown
   ## PR Notes
   - Used `--no-verify` for commits abc123 and def456 due to ongoing refactoring
   - All quality violations fixed in final commit xyz789
   ```

## Troubleshooting Guide

### Issue 1: Pre-commit Hooks Not Running

**Symptoms:** Commits succeed without any quality checks running

**Causes:**
- Pre-commit not installed
- Git hooks not initialized

**Solution:**
```bash
# Verify pre-commit is installed
pre-commit --version

# If not installed
pip install pre-commit

# Initialize git hooks
pre-commit install

# Verify installation
ls -la .git/hooks/pre-commit
# Should show: .git/hooks/pre-commit -> ~/.../pre-commit
```

### Issue 2: Tool Not Found Errors

**Symptoms:**
```
mypy....................................................................Failed
- hook id: mypy
- exit code: 127

/bin/sh: mypy: command not found
```

**Causes:** Required tool not installed in environment

**Solution:**
```bash
# For Python tools
cd packages/python/zlibrary-downloader
pip install -e ".[dev]"

# For Rust tools (rust-code-analysis)
cargo install rust-code-analysis-cli

# Verify installations
mypy --version
flake8 --version
black --version
radon --version
rust-code-analysis-cli --version
```

### Issue 3: Pre-commit is Too Slow

**Symptoms:** Pre-commit takes >30 seconds to run

**Solutions:**

1. **Use file-specific commits** instead of committing entire codebase:
   ```bash
   git add specific_file.py
   git commit -m "Fix specific issue"
   ```

2. **Enable pre-commit caching** (enabled by default):
   ```bash
   # Clear cache if stale
   pre-commit clean
   ```

3. **Skip slow hooks temporarily** during development:
   ```bash
   # Skip all hooks
   git commit --no-verify

   # Run only specific hook
   SKIP=cargo-clippy,mypy git commit
   ```

4. **Run full validation before PR** instead of every commit:
   ```bash
   # During development: quick commits
   git commit --no-verify

   # Before pushing: full validation
   pre-commit run --all-files
   ```

### Issue 4: Black and Flake8 Conflicts

**Symptoms:**
```
black...................................................................Passed
flake8..................................................................Failed
- hook id: flake8
- exit code: 1

file.py:42:80: E501 line too long (105 > 100 characters)
```

**Cause:** Black reformatted code but line is still too long (rare edge case)

**Solution:**
```bash
# Black should have fixed this, but if not:
# 1. Manually break the line
# 2. Add # noqa: E501 comment if truly necessary
some_very_long_line()  # noqa: E501
```

### Issue 5: Type Hint Errors After Adding Hints

**Symptoms:**
```
mypy....................................................................Failed
- hook id: mypy
- exit code: 1

zlibrary_downloader/client.py:123: error: Argument 1 to "search" has incompatible type "str"; expected "Optional[str]"
```

**Cause:** Type annotations don't match actual function signatures or usage

**Solution:**
```python
# Incorrect type hint
def search(query: str) -> List[Dict[str, str]]:
    if query is None:  # This contradicts the type hint
        return []

# Corrected type hint
from typing import Optional, List, Dict

def search(query: Optional[str]) -> List[Dict[str, str]]:
    if query is None:
        return []
    # ... rest of function
```

**Debugging Tips:**
```bash
# Run mypy with more verbose output
mypy --show-error-codes --pretty zlibrary_downloader

# Check specific file
mypy zlibrary_downloader/client.py
```

### Issue 6: Complexity Violations Hard to Fix

**Symptoms:** Function has complexity >10 but refactoring is unclear

**Solution Strategy:**

1. **Identify decision points:**
   ```bash
   # Use radon to see complexity breakdown
   radon cc -s zlibrary_downloader/tui.py
   ```

2. **Extract conditional logic:**
   - Move nested if/else into separate validation functions
   - Use early returns (guard clauses)

3. **Simplify boolean expressions:**
   ```python
   # Before (complex)
   if user is not None and user.is_active and (user.role == 'admin' or user.role == 'moderator'):
       # ...

   # After (simple)
   is_privileged_user = user is not None and user.is_active and user.role in ['admin', 'moderator']
   if is_privileged_user:
       # ...
   ```

4. **Use lookup tables instead of if/elif chains:**
   ```python
   # Before (high complexity)
   if action == 'create':
       return create_item()
   elif action == 'update':
       return update_item()
   elif action == 'delete':
       return delete_item()
   # ... 10 more cases

   # After (low complexity)
   actions = {
       'create': create_item,
       'update': update_item,
       'delete': delete_item,
       # ... 10 more cases
   }
   handler = actions.get(action, default_handler)
   return handler()
   ```

### Issue 7: Permission Denied on Scripts

**Symptoms:**
```
scripts/check_rust_complexity.sh........................................Failed
- hook id: rust-complexity
- exit code: 126

/bin/sh: scripts/check_rust_complexity.sh: Permission denied
```

**Cause:** Scripts not executable

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py

# Verify permissions
ls -la scripts/
# Should show: -rwxr-xr-x
```

### Issue 8: Git Hooks Outdated After Pre-commit Update

**Symptoms:** Hooks not reflecting latest `.pre-commit-config.yaml` changes

**Solution:**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update to latest hook versions
pre-commit autoupdate

# Clean cache and reinstall
pre-commit clean
pre-commit install --install-hooks
```

### Issue 9: Emergency: Need to Commit NOW

**Situation:** Production is down, need to deploy hotfix immediately

**Procedure:**
```bash
# 1. Bypass pre-commit (document reason!)
git commit --no-verify -m "HOTFIX: Critical production bug #123 (bypassed QA)"

# 2. Push to production
git push origin main

# 3. Create follow-up issue
gh issue create --title "Fix QA violations in hotfix abc123" --label "technical-debt"

# 4. Fix violations in next commit
# ... make fixes ...
git commit -m "Fix QA violations from hotfix abc123 (closes #456)"
```

## Development Workflow

### Standard Workflow with QA Compliance

```bash
# 1. Create feature branch
git checkout -b feature/new-authentication

# 2. Make code changes
# ... edit files ...

# 3. Run manual checks during development (optional but recommended)
pre-commit run --all-files

# 4. Stage changes
git add .

# 5. Commit (pre-commit hooks run automatically)
git commit -m "feat: Add OAuth2 authentication support"

# If hooks fail:
# 6a. Fix issues based on error messages
# 6b. Stage fixes
git add .
# 6c. Retry commit
git commit -m "feat: Add OAuth2 authentication support"

# 7. Push to remote (run full validation first)
pre-commit run --all-files
git push origin feature/new-authentication

# 8. Create pull request
gh pr create --title "Add OAuth2 authentication support" --body "..."

# 9. Wait for CI/CD checks and code review
```

### Iterative Development Workflow

For large refactorings or feature work spanning multiple commits:

```bash
# 1. WIP commits during development (bypass if needed)
git commit --no-verify -m "WIP: Refactoring authentication (1/5)"
git commit --no-verify -m "WIP: Refactoring authentication (2/5)"
# ... more WIP commits ...

# 2. Run full validation before finalizing
pre-commit run --all-files

# 3. Fix all issues found
# ... fix violations ...

# 4. Final commit with full validation
git add .
git commit -m "refactor: Complete authentication module refactoring"

# 5. Optionally squash WIP commits before PR
git rebase -i origin/main
# Squash WIP commits into final commit
```

### Testing Workflow

```bash
# 1. Make code changes
# ... edit files ...

# 2. Run unit tests
cd packages/python/zlibrary-downloader
pytest

# 3. Check test coverage
pytest --cov --cov-report=html
open htmlcov/index.html

# 4. Run quality checks
pre-commit run --all-files

# 5. Commit if all pass
git add .
git commit -m "test: Add tests for new authentication flow"
```

## CI/CD Integration

The same quality tools used locally can be integrated into CI/CD pipelines:

### GitHub Actions Example

```yaml
name: QA Compliance

on: [push, pull_request]

jobs:
  rust-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          components: rustfmt, clippy

      - name: Rust type checking
        run: cargo check --manifest-path packages/rust/Cargo.toml

      - name: Rust linting
        run: cargo clippy --manifest-path packages/rust/Cargo.toml -- -D warnings

      - name: Rust formatting
        run: cargo fmt --manifest-path packages/rust/Cargo.toml --check

      - name: Rust tests
        run: cargo test --manifest-path packages/rust/Cargo.toml

  python-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          cd packages/python/zlibrary-downloader
          pip install -e ".[dev]"

      - name: Python type checking
        run: |
          cd packages/python/zlibrary-downloader
          mypy zlibrary_downloader

      - name: Python linting
        run: flake8 packages/python/zlibrary-downloader/zlibrary_downloader/

      - name: Python formatting
        run: black --check packages/python/zlibrary-downloader/zlibrary_downloader/

      - name: Python tests
        run: |
          cd packages/python/zlibrary-downloader
          pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./packages/python/zlibrary-downloader/coverage.xml

  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit on all files
        run: pre-commit run --all-files
```

### Benefits of CI/CD Integration

1. **Consistency:** Same checks locally and in CI/CD
2. **Enforcement:** Catch bypassed commits (--no-verify)
3. **Team Visibility:** All team members see quality metrics
4. **Automated Reporting:** Coverage reports, complexity trends
5. **Merge Protection:** Block PRs that don't meet quality standards

---

## Additional Resources

- **Product Vision:** `product.md` - Product principles and quality standards
- **Technical Standards:** `tech.md` - Tool selection and technical guidelines
- **Project Structure:** `structure.md` - Code organization and conventions
- **Quick Start:** `README.md` - Setup instructions and common commands
- **Spec Requirements:** `.spec-workflow/specs/qa-compliance/requirements.md` - Detailed requirements
- **Spec Design:** `.spec-workflow/specs/qa-compliance/design.md` - Architecture and implementation details

## Questions or Issues?

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](#troubleshooting-guide) above
2. Search existing GitHub issues
3. Create a new issue with the `qa-compliance` label
4. Reach out to the development team

**Remember:** Quality checks are here to help, not hinder. They catch issues early when they're cheap to fix. If a check seems wrong, let's discuss and improve it together!
