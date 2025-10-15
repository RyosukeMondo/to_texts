# Project Structure

## Directory Organization

```
to_texts/                              # Monorepo root
├── .env.example                       # Environment variables template
├── .gitignore                         # Root gitignore
├── README.md                          # Main project documentation
│
├── .spec-workflow/                    # Spec workflow configuration
│   ├── steering/                      # Steering documents
│   │   ├── product.md                 # Product overview
│   │   ├── tech.md                    # Technology stack
│   │   └── structure.md               # This document
│   └── templates/                     # Document templates
│
├── docs/                              # Additional documentation
│   ├── text-extractor.md
│   └── zlibrary-downloader.md
│
├── packages/                          # All sub-projects
│   ├── rust/                          # Rust workspace
│   │   ├── Cargo.toml                 # Workspace manifest
│   │   ├── Cargo.lock                 # Dependency lock file
│   │   ├── target/                    # Build artifacts (gitignored)
│   │   │   ├── debug/                 # Debug builds
│   │   │   └── release/               # Release builds
│   │   │
│   │   └── text-extractor/            # PDF/EPUB text extraction tool
│   │       ├── Cargo.toml             # Package manifest
│   │       ├── README.md              # Package documentation
│   │       ├── src/
│   │       │   └── main.rs            # Entry point and core logic
│   │       └── test_epub.rs           # Integration tests
│   │
│   └── python/                        # Python projects
│       └── zlibrary-downloader/       # Z-Library downloader tool
│           ├── pyproject.toml         # Package configuration (PEP 517/518)
│           ├── requirements.txt       # Dependencies
│           ├── README.md              # Package documentation
│           │
│           ├── scripts/               # Utility scripts
│           │   ├── setup.sh           # Virtual environment setup
│           │   └── run.sh             # CLI wrapper script
│           │
│           ├── venv/                  # Virtual environment (gitignored)
│           │
│           └── zlibrary_downloader/   # Python package
│               ├── __init__.py        # Package initialization
│               ├── cli.py             # CLI entry point and argument parsing
│               ├── client.py          # Z-Library API wrapper
│               └── tui.py             # Rich-based TUI interface
│
├── downloads/                         # Downloaded books (gitignored)
└── tmp/                               # Temporary/extracted files (gitignored)
```

## Naming Conventions

### Files

**Rust:**
- **Modules**: `snake_case` (e.g., `main.rs`, `pdf_utils.rs`)
- **Tests**: `test_*.rs` or inline with `#[cfg(test)]` modules
- **Constants**: Follow Rust standard (`Cargo.toml`, `Cargo.lock`)

**Python:**
- **Modules**: `snake_case` (e.g., `cli.py`, `client.py`, `tui.py`)
- **Packages**: `snake_case` directories with `__init__.py`
- **Tests**: `test_*.py` or `*_test.py` in `tests/` directory
- **Scripts**: `kebab-case.sh` for shell scripts

**Documentation:**
- **Markdown**: `kebab-case.md` (e.g., `text-extractor.md`)
- **README files**: `README.md` (uppercase)

### Code

**Rust:**
- **Structs/Enums/Traits**: `PascalCase` (e.g., `Args`, `Result`)
- **Functions/Methods**: `snake_case` (e.g., `extract_pdf_text`, `generate_output_path`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)
- **Variables**: `snake_case` (e.g., `pdf_path`, `output_dir`)
- **Type Parameters**: Single uppercase letter or `PascalCase` (e.g., `T`, `Item`)

**Python:**
- **Classes**: `PascalCase` (e.g., `Zlibrary`, `ZLibraryTUI`)
- **Functions/Methods**: `snake_case` (e.g., `search_books`, `download_book`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `FORMATS`, `LANGUAGES`)
- **Variables**: `snake_case` (e.g., `z_client`, `book_num`)
- **Private members**: Prefix with single underscore (e.g., `_loggedin`, `__makePostRequest`)

## Import Patterns

### Rust Import Order

```rust
// 1. Standard library
use std::fs;
use std::path::{Path, PathBuf};

// 2. External crates (alphabetical)
use anyhow::{Context, Result};
use clap::Parser;
use walkdir::WalkDir;

// 3. Internal modules (if any)
// use crate::utils;
// use crate::models::Book;
```

### Python Import Order

```python
# 1. Standard library
import os
import sys
import argparse

# 2. External dependencies (alphabetical)
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# 3. Internal modules (relative imports)
from .client import Zlibrary
from .tui import ZLibraryTUI
```

### Module Organization

**Rust:**
- All modules use absolute imports from crate root
- Use `crate::` for internal modules
- External dependencies via Cargo.toml

**Python:**
- Absolute imports for external dependencies
- Relative imports within package (`.client`, `.tui`)
- Editable install for development (`pip install -e .`)

## Code Structure Patterns

### Rust Module Organization

**File Structure Pattern:**
```rust
// 1. Imports and dependencies
use std::path::Path;
use anyhow::Result;

// 2. Type definitions and structs
#[derive(Parser, Debug)]
struct Args {
    // fields
}

// 3. Main entry point (for main.rs)
fn main() -> Result<()> {
    // implementation
}

// 4. Public functions (business logic)
fn extract_pdf_text(pdf_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    // implementation
}

// 5. Private helper functions
fn strip_html_tags(html: &str) -> String {
    // implementation
}

// 6. Tests (optional inline)
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_something() {
        // test implementation
    }
}
```

### Python Module Organization

**File Structure Pattern:**
```python
# 1. Module docstring
"""
Module description and purpose
"""

# 2. Imports
import os
from typing import Optional

# 3. Constants
FORMATS = ['pdf', 'epub', 'mobi']
DEFAULT_LIMIT = 20

# 4. Classes
class ZLibraryTUI:
    """Class docstring"""

    def __init__(self, client):
        """Constructor"""
        pass

    def public_method(self):
        """Public method"""
        pass

    def _private_method(self):
        """Private helper method"""
        pass

# 5. Module-level functions
def helper_function(arg1, arg2):
    """Function docstring"""
    pass

# 6. Main execution guard
if __name__ == "__main__":
    main()
```

### Function Organization Principles

**Both Languages:**
```
1. Docstring/documentation comment
2. Input validation and early returns
3. Core logic (single level of abstraction)
4. Error handling with context
5. Return result
```

**Example (Rust):**
```rust
/// Extract text from a PDF file
fn extract_pdf_text(pdf_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    // 1. Validate inputs
    if !pdf_path.exists() {
        anyhow::bail!("PDF does not exist");
    }

    // 2. Core logic
    let text = pdf_extract::extract_text(pdf_path)
        .context("Failed to extract text")?;

    // 3. Generate output
    let output_path = generate_output_path(pdf_path, output_dir, "txt")?;

    // 4. Write result
    fs::write(&output_path, text)
        .context("Failed to write output")?;

    // 5. Return
    Ok(output_path)
}
```

### File Organization Principles

1. **Single Responsibility**: Each file has one clear purpose
   - `main.rs`: Entry point and orchestration
   - `cli.py`: Argument parsing and mode selection
   - `client.py`: API communication only
   - `tui.py`: UI presentation only

2. **Separation of Concerns**:
   - Business logic separate from UI
   - API client separate from CLI
   - File I/O separate from processing logic

3. **Dependency Direction**:
   - CLI depends on client and TUI
   - TUI depends on client
   - Client has no dependencies on CLI/TUI

## Code Organization Principles

### Single Responsibility Principle

**Each file has one clear purpose:**
- `main.rs`: PDF/EPUB extraction orchestration
- `cli.py`: Command-line interface and mode routing
- `client.py`: Z-Library API wrapper
- `tui.py`: Interactive terminal user interface

### Modularity

**Reusable components:**
- Text extraction functions are pure and testable
- API client can be used independently of CLI/TUI
- TUI can be instantiated programmatically

### Testability

**Structure for testing:**
- Pure functions for transformation logic (e.g., `strip_html_tags`)
- Dependency injection for API clients
- Separate I/O from logic where possible
- Integration tests in separate files

### Consistency

**Project-wide patterns:**
- Error handling: Result types (Rust), exceptions (Python)
- Configuration: Environment variables via .env
- Output: User-specified directories
- Logging: stdout/stderr conventions

## Module Boundaries

### Rust Workspace Boundaries

**Current Structure:**
- Single crate: `text-extractor`
- Future: Additional crates for shared utilities

**Dependency Direction:**
```
text-extractor
  ├── pdf-extract (external)
  ├── epub (external)
  └── shared utilities (future internal crate)
```

### Python Package Boundaries

**Package Structure:**
```
zlibrary_downloader/
  ├── __init__.py      # Package exports
  ├── cli.py           # Entry point (depends on client, tui)
  ├── client.py        # API wrapper (no internal dependencies)
  └── tui.py           # UI layer (depends on client)
```

**Dependency Direction:**
```
cli.py → client.py
cli.py → tui.py → client.py
```

### Cross-Language Boundaries

**Integration Point:**
- Shell scripts/automation can call both tools
- File system as the interface (downloads → tmp)
- No direct code dependencies between Rust and Python

**Pipeline Pattern:**
```
Z-Library Downloader → downloads/ → Text Extractor → tmp/
```

### Public API vs Internal

**Rust (text-extractor):**
- **Public**: Command-line interface via clap
- **Internal**: All functions (single-file design)

**Python (zlibrary-downloader):**
- **Public**:
  - CLI entry point: `zlibrary-downloader` command
  - `Zlibrary` class for programmatic use
  - `ZLibraryTUI` class for TUI integration
- **Private**:
  - Internal API methods (prefixed with `_` or `__`)
  - Helper functions in modules

## Code Size Guidelines

### File Size Limits

**Maximum: 400 lines per file**
- Excludes blank lines and comments
- Excludes generated code
- Excludes test files
- Files exceeding limit must be refactored into modules

**Current Status:**
- `main.rs`: 206 lines ✓
- `cli.py`: 340 lines ✓
- `client.py`: 362 lines ✓
- `tui.py`: 364 lines ✓

### Function/Method Size Limits

**Maximum: 30 lines per function**
- Excludes signature and closing brace
- Excludes comments and blank lines
- Complex functions must be decomposed

**Audit Required:** Current codebase needs function-level audit

### Complexity Limits

**Maximum Cyclomatic Complexity: 10**
- Apply to all functions in Rust and Python
- Use `cargo-complexity` (Rust) and `radon` (Python)
- Functions exceeding limit must be refactored

**Audit Required:** Complexity analysis needed for compliance

### Nesting Depth

**Maximum: 4 levels of nesting**
- Prefer early returns over deep nesting
- Extract nested logic into helper functions
- Use guard clauses to reduce nesting

## Dashboard/Monitoring Structure

### Python TUI Structure

```
zlibrary_downloader/
└── tui.py                         # Self-contained TUI module
    ├── ZLibraryTUI class          # Main TUI interface
    ├── Rich components            # Tables, panels, prompts
    └── Progress indicators        # Spinners, status
```

**Separation of Concerns:**
- TUI is independent module with single responsibility
- Can be used standalone via `--tui` flag
- No business logic in TUI (delegates to client)
- Pure presentation layer

**Entry Points:**
```python
# Direct TUI mode
./scripts/run.sh --tui

# Programmatic use
from zlibrary_downloader.tui import ZLibraryTUI
tui = ZLibraryTUI(z_client)
tui.run()
```

### CLI Output Structure

**Text Extractor (Rust):**
- Stdout: Progress messages, success notifications
- Stderr: Error messages with context
- Summary: Statistics at completion

**Z-Library Downloader (Python):**
- Stdout: Search results, download status (CLI mode)
- Stderr: Error messages and warnings
- Rich formatting: Colors and tables (TUI mode)

## Documentation Standards

### Code Documentation

**Rust:**
- **Public items**: `///` doc comments with examples
- **Module-level**: `//!` inner doc comments
- **Complex logic**: `//` inline comments
- **Generate docs**: `cargo doc --open`

**Python:**
- **Classes/Functions**: Docstrings (triple quotes)
- **Modules**: Module-level docstring at top
- **Complex logic**: `#` inline comments
- **Format**: Google or NumPy style

### README Files

**Required for:**
- Monorepo root (main README.md)
- Each package (packages/rust/text-extractor/README.md)
- Each Python project (packages/python/zlibrary-downloader/README.md)

**README Structure:**
```markdown
# Project Name

## Description
## Features
## Installation
## Usage
## Examples
## Configuration
## License
```

### Inline Comments

**When to comment:**
- Complex algorithms or business logic
- Non-obvious workarounds or hacks
- TODOs and FIXMEs with issue references
- Performance optimizations

**When NOT to comment:**
- Self-explanatory code
- Redundant descriptions of what code does
- Commented-out code (delete instead)

## Testing Structure

### Rust Tests

**Location:**
- Unit tests: Inline with `#[cfg(test)]` modules
- Integration tests: `tests/` directory (future)

**Structure:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_strip_html_tags() {
        let html = "<p>Hello</p>";
        let result = strip_html_tags(html);
        assert_eq!(result, "Hello");
    }
}
```

### Python Tests

**Location:**
- Unit tests: `tests/` directory (to be created)
- Test files: `test_*.py` naming convention

**Structure:**
```python
import pytest
from zlibrary_downloader.client import Zlibrary

def test_login():
    # Test implementation
    pass

def test_search():
    # Test implementation
    pass
```

**Testing Standards:**
- Target >80% code coverage
- Test public APIs thoroughly
- Mock external dependencies (Z-Library API)
- Property-based testing for pure functions

## Configuration Management

### Environment Variables

**Location:** Root `.env` file (gitignored)

**Structure:**
```bash
# Z-Library credentials (choose one method)
ZLIBRARY_EMAIL=user@example.com
ZLIBRARY_PASSWORD=password

# OR

ZLIBRARY_REMIX_USERID=12345
ZLIBRARY_REMIX_USERKEY=abc123def456
```

**Loading:**
- Python: `python-dotenv` library
- Rust: Not required (no credentials needed)

### Build Configuration

**Rust:**
- `Cargo.toml`: Workspace and package configuration
- Build profiles: debug (default), release (optimized)

**Python:**
- `pyproject.toml`: Package metadata and dependencies
- `requirements.txt`: Pinned dependencies for reproducibility

## Quality Enforcement

### Pre-commit Hooks

**Configuration:** `.pre-commit-config.yaml`

**Checks:**
```yaml
repos:
  - repo: local
    hooks:
      # Rust checks
      - id: cargo-check
      - id: cargo-clippy
      - id: cargo-fmt
      - id: cargo-complexity

      # Python checks
      - id: mypy
      - id: flake8
      - id: black
      - id: radon-complexity

      # Code metrics
      - id: line-count-validator
      - id: function-size-validator
```

### Continuous Integration (Future)

**GitHub Actions Workflow:**
```yaml
- Rust: cargo test, clippy, fmt check
- Python: pytest, mypy, flake8, black check
- Complexity validation
- Code coverage reporting
```

## Migration Path

### Current State → Compliant State

**Action Items:**
1. **Add Type Hints (Python)**: Complete type annotations for mypy
2. **Complexity Audit**: Analyze all functions, refactor violations
3. **Line Count Audit**: Check all files and functions
4. **Pre-commit Setup**: Install and configure hooks
5. **Test Coverage**: Write missing tests (target >80%)
6. **Documentation**: Add docstrings and comments

**Timeline:** Target v0.2.0 for full compliance
