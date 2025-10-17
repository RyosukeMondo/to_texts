# to_texts

A monorepo containing tools for working with ebooks and documents.

## Projects

### 🦀 Rust: Text Extractor
**Location:** `packages/rust/text-extractor/`

A high-performance CLI tool for extracting text from PDF and EPUB files.

**Features:**
- Extract text from PDF files (with proper encoding support)
- Extract text from EPUB files
- Recursive directory processing
- Clean, formatted text output

**Quick Start:**
```bash
cd packages/rust
cargo build --release
cargo run --release -- --target /path/to/files --output ./extracted
```

**Documentation:** [Text Extractor README](packages/rust/text-extractor/README.md)

---

### 🐍 Python: Z-Library Downloader
**Location:** `packages/python/zlibrary-downloader/`

A feature-rich CLI and TUI tool for searching and downloading books from Z-Library.

**Features:**
- Beautiful interactive TUI (Text User Interface)
- Advanced search with filters (format, year, language)
- Command-line interface for automation
- Download books in various formats
- **Local database for cataloging and organizing your collection**
- Reading lists and saved books management
- Download tracking and search history

**Quick Start:**
```bash
cd packages/python/zlibrary-downloader
./scripts/setup.sh
# Configure credentials in root .env file
./scripts/run.sh --tui
```

**Documentation:** [Z-Library Downloader README](packages/python/zlibrary-downloader/README.md)

#### Database Features

The Z-Library Downloader includes a powerful local SQLite database for managing your book collection:

- **Catalog Building:** Store search results locally for offline browsing
- **Advanced Filtering:** Browse by language, year, format, author, or text query
- **Reading Lists:** Create and manage multiple reading lists with ordered books
- **Saved Books:** Mark favorites with notes, tags, and priority levels
- **Download Tracking:** Automatic tracking of all downloads with history
- **Import/Export:** Backup and restore your catalog in JSON/CSV formats
- **Statistics:** View detailed stats about your collection

**Database Quick Start:**
```bash
# Initialize database
zlibrary-downloader db init

# Search and store results
zlibrary-downloader search --title "Python" --save-db

# Browse your catalog
zlibrary-downloader db browse --language english --format pdf

# Create a reading list
zlibrary-downloader db list-create "To Read"
zlibrary-downloader db list-add "To Read" <book-id>

# Export your catalog
zlibrary-downloader db export --output my_books.json
```

**Full Database Guide:** [Database Features Guide](docs/database-guide.md)

---

## Repository Structure

```
to_texts/
├── README.md                           # This file
├── .gitignore                          # Root gitignore
├── .env.example                        # Environment variables template
│
├── docs/                               # Documentation
│   ├── text-extractor.md
│   └── zlibrary-downloader.md
│
├── packages/                           # All sub-projects
│   ├── rust/                           # Rust workspace
│   │   ├── Cargo.toml                  # Workspace manifest
│   │   └── text-extractor/             # PDF/EPUB → Text CLI
│   │       ├── Cargo.toml
│   │       ├── src/
│   │       └── README.md
│   │
│   └── python/                         # Python projects
│       └── zlibrary-downloader/        # Z-Library downloader
│           ├── zlibrary_downloader/    # Python package
│           ├── scripts/                # Setup and run scripts
│           ├── requirements.txt
│           ├── pyproject.toml
│           └── README.md
│
├── downloads/                          # Downloaded files (gitignored)
└── tmp/                                # Temporary files (gitignored)
```

## Workflow Example

1. **Download books** using the Python Z-Library downloader:
   ```bash
   cd packages/python/zlibrary-downloader
   ./scripts/run.sh --title "Python Programming" --format pdf --download
   ```

2. **Extract text** from downloaded PDFs using the Rust text extractor:
   ```bash
   cd packages/rust
   cargo run --release -- --target ../../downloads/ --output ../../tmp/
   ```

## Setup

### Prerequisites
- **Rust:** Install from [rustup.rs](https://rustup.rs/)
- **Python 3.8+:** System Python installation

### Environment Variables
Copy `.env.example` to `.env` at the repository root and configure:
```bash
cp .env.example .env
# Edit .env with your Z-Library credentials
```

### Build All Projects
```bash
# Build Rust workspace
cd packages/rust
cargo build --release

# Setup Python package
cd ../python/zlibrary-downloader
./scripts/setup.sh
```

## Quality Assurance

This repository enforces code quality standards through automated pre-commit hooks. All commits are validated for type safety, code style, complexity, and maintainability.

### Quick Setup

Install QA tools and setup git hooks:

```bash
# Install pre-commit framework
pip install pre-commit

# Install Rust analysis tools
cargo install rust-code-analysis-cli

# Install Python development dependencies
cd packages/python/zlibrary-downloader
pip install -e ".[dev]"
cd ../../..

# Setup git hooks
pre-commit install
```

### Quality Standards

The following standards are automatically enforced on every commit:

**Code Metrics:**
- Maximum 400 lines per file
- Maximum 30 lines per function
- Maximum cyclomatic complexity of 10

**Rust Checks:**
- Type checking (`cargo check`)
- Linting (`cargo clippy`)
- Formatting (`rustfmt`)
- Complexity analysis

**Python Checks:**
- Type checking (`mypy --strict`)
- Linting (`flake8`)
- Formatting (`black --check`)
- Complexity analysis (`radon`)

### Manual Quality Checks

Run quality checks manually without committing:

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Run specific hooks
pre-commit run mypy --all-files
pre-commit run cargo-clippy --all-files

# Rust checks
cd packages/rust
cargo check
cargo clippy
cargo fmt --check
cargo test

# Python checks
cd packages/python/zlibrary-downloader
mypy zlibrary_downloader/
flake8 zlibrary_downloader/
black --check zlibrary_downloader/
pytest --cov --cov-report=html
```

### Auto-Fixing Issues

Some tools can automatically fix violations:

```bash
# Auto-format Rust code
cd packages/rust
cargo fmt

# Auto-format Python code
cd packages/python/zlibrary-downloader
black zlibrary_downloader/

# Auto-fix some flake8 issues
autopep8 --in-place --aggressive zlibrary_downloader/
```

### Troubleshooting

**Pre-commit hooks not running:**
```bash
# Verify installation
pre-commit --version

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

**Tool not found errors:**
```bash
# Rust tools
cargo install rust-code-analysis-cli

# Python tools (all at once)
cd packages/python/zlibrary-downloader
pip install -e ".[dev]"

# Python tools (individually)
pip install mypy>=1.8.0 black>=24.0.0 flake8>=7.0.0 radon>=6.0.0
```

**Emergency bypass (use sparingly):**
```bash
# Skip hooks for urgent WIP commits on feature branches
git commit --no-verify -m "WIP: fix needed"

# Note: Violations must be fixed before merging to main
```

**Performance issues:**
```bash
# Run hooks only on staged files (default behavior)
git add <files>
git commit

# Skip slow hooks temporarily during development
SKIP=rust-complexity,radon-complexity git commit
```

### Development Workflow

1. Make code changes
2. Stage changes: `git add <files>`
3. Attempt commit: `git commit -m "message"`
4. If hooks fail:
   - Review error messages
   - Fix violations
   - Repeat from step 2
5. When all hooks pass, commit succeeds

For detailed QA documentation, see: `docs/qa-compliance.md`

## Contributing

This is a monorepo managed with:
- **Rust:** Cargo workspaces
- **Python:** pip with editable installs

When adding new projects:
1. Add Rust crates to `packages/rust/` and update workspace `Cargo.toml`
2. Add Python packages to `packages/python/` with their own `pyproject.toml`

**Code Quality:**
- All code must pass pre-commit hooks (see Quality Assurance section)
- Maintain test coverage ≥80% for Python code
- Follow existing code style and patterns

## License

MIT OR Apache-2.0

## Credits

- **Z-Library API:** Uses the unofficial API wrapper by [bipinkrish](https://github.com/bipinkrish/Zlibrary-API)
- **PDF Extraction:** Powered by [pdf-extract](https://crates.io/crates/pdf-extract)
