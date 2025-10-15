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

**Quick Start:**
```bash
cd packages/python/zlibrary-downloader
./scripts/setup.sh
# Configure credentials in root .env file
./scripts/run.sh --tui
```

**Documentation:** [Z-Library Downloader README](packages/python/zlibrary-downloader/README.md)

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

## Contributing

This is a monorepo managed with:
- **Rust:** Cargo workspaces
- **Python:** pip with editable installs

When adding new projects:
1. Add Rust crates to `packages/rust/` and update workspace `Cargo.toml`
2. Add Python packages to `packages/python/` with their own `pyproject.toml`

## License

MIT OR Apache-2.0

## Credits

- **Z-Library API:** Uses the unofficial API wrapper by [bipinkrish](https://github.com/bipinkrish/Zlibrary-API)
- **PDF Extraction:** Powered by [pdf-extract](https://crates.io/crates/pdf-extract)
