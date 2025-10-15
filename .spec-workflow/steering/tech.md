# Technology Stack

## Project Type
Multi-language monorepo containing two standalone CLI tools:
- **Text Extractor**: High-performance command-line tool for extracting text from PDF and EPUB files (Rust)
- **Z-Library Downloader**: Interactive TUI and CLI tool for searching and downloading books (Python)

Both tools are designed for local execution with file system integration and can be used independently or in a pipeline workflow.

## Core Technologies

### Primary Language(s)

**Rust (Text Extractor)**
- **Version**: Rust 2021 Edition
- **Compiler**: rustc via cargo
- **Package Manager**: Cargo
- **Workspace**: Cargo workspaces for multi-crate management

**Python (Z-Library Downloader)**
- **Version**: Python 3.8+
- **Runtime**: CPython
- **Package Manager**: pip
- **Build System**: setuptools with pyproject.toml (PEP 517/518)

### Key Dependencies/Libraries

**Rust Dependencies:**
- **clap 4.5**: Command-line argument parsing with derive macros
- **anyhow 1.0**: Ergonomic error handling with context propagation
- **walkdir 2.5**: Recursive directory traversal for batch processing
- **pdf-extract 0.7**: PDF text extraction with encoding support
- **epub 2.1**: EPUB parsing and content extraction

**Python Dependencies:**
- **requests ≥2.31.0**: HTTP client for Z-Library API interactions
- **python-dotenv ≥1.0.0**: Environment variable management for credentials
- **rich ≥13.7.0**: Terminal UI framework for interactive TUI mode

**Development Dependencies:**
- **Python Dev Tools**: pytest, black, flake8, mypy
- **Rust Dev Tools**: cargo-clippy, rustfmt, cargo-test

### Application Architecture

**Architecture Pattern**: Standalone CLI with modular function decomposition

**Text Extractor (Rust):**
- **Entry Point**: `main.rs` with clap-based argument parsing
- **Processing Model**: Synchronous, iterative file processing
- **Error Handling**: Result-based error propagation with anyhow contexts
- **File Operations**: Recursive directory walking with format detection

**Z-Library Downloader (Python):**
- **Module Structure**:
  - `client.py`: Z-Library API wrapper (adapted from bipinkrish/Zlibrary-API)
  - `tui.py`: Rich-based interactive interface
  - `cli.py`: Command-line entry point and mode orchestration
- **Operation Modes**:
  - TUI mode (interactive with rich UI)
  - CLI mode (direct search and download)
  - Classic interactive mode (fallback)

### Data Storage

**Text Extractor:**
- **Input**: PDF/EPUB files from specified directories
- **Output**: Plain text files (.txt) with UTF-8 encoding
- **Storage**: File system (user-specified output directory)
- **No persistent state**: Stateless processing

**Z-Library Downloader:**
- **Downloads**: Books saved to `downloads/` directory (configurable)
- **Credentials**: Stored in `.env` file (never committed)
- **Session Management**: Cookie-based authentication with Z-Library API
- **Data Formats**: JSON responses from API, binary book files

### External Integrations

**Z-Library API:**
- **Protocol**: HTTPS/REST
- **Domain**: 1lib.sk (configurable)
- **Authentication Methods**:
  - Email/password login
  - Remix token (userid + userkey)
- **API Endpoints**:
  - `/eapi/user/login`: User authentication
  - `/eapi/book/search`: Book search with filters
  - `/eapi/book/{id}/{hash}/file`: Book download
  - `/eapi/user/profile`: User profile and quota information
- **Rate Limiting**: Subject to Z-Library's daily download quotas

**No External Dependencies for Text Extractor:**
- Operates entirely offline on local files

### Monitoring & Dashboard Technologies

**Z-Library Downloader (TUI Mode):**
- **Dashboard Framework**: Rich library (terminal-based)
- **Components**:
  - Interactive prompts with validation
  - Progress spinners for async operations
  - Tables for search results display
  - Panels for structured information
- **State Management**: In-memory session state
- **Real-time Updates**: Synchronous with progress indicators

**Text Extractor:**
- **Dashboard**: CLI with stdout/stderr logging
- **Progress Reporting**: File-by-file processing status
- **Summary Statistics**: Processed/error counts on completion

## Development Environment

### Build & Development Tools

**Rust Workspace:**
- **Build System**: Cargo with workspace configuration
- **Workspace Root**: `packages/rust/Cargo.toml`
- **Build Commands**:
  - `cargo build --release`: Production builds
  - `cargo run -- <args>`: Development runs
  - `cargo test`: Run test suite
- **Target Directory**: `target/` (debug and release profiles)

**Python Package:**
- **Build Backend**: setuptools
- **Setup Scripts**: `scripts/setup.sh` for virtual environment
- **Run Scripts**: `scripts/run.sh` for CLI execution
- **Virtual Environment**: `venv/` directory (gitignored)
- **Editable Install**: `pip install -e .` for development

### Code Quality Tools

**Rust Quality Assurance:**
- **Linting**: `cargo clippy` with strict lints
- **Formatting**: `rustfmt` with default configuration
- **Type Checking**: Compile-time via rustc (static typing)
- **Complexity Analysis**: `cargo-complexity` for cyclomatic complexity
- **Testing**: `cargo test` with integration tests

**Python Quality Assurance:**
- **Type Checking**: `mypy` with strict mode enabled
- **Linting**: `flake8` with line length and complexity rules
- **Formatting**: `black` (line-length: 100, target: py38)
- **Complexity Analysis**: `radon` for cyclomatic complexity measurement
- **Testing**: `pytest` for unit and integration tests

**Pre-commit Framework:**
- **Tool**: `pre-commit` git hooks
- **Checks**:
  - Type checking (cargo check, mypy)
  - Linting (clippy, flake8)
  - Formatting verification (rustfmt, black)
  - Cyclomatic complexity validation (≤10 per function)
  - Line count validation (≤400 per file, ≤30 per function)
- **Configuration**: `.pre-commit-config.yaml`

**Code Metrics Enforcement:**
- **File Size**: Maximum 400 lines per file
- **Function Size**: Maximum 30 lines per function
- **Cyclomatic Complexity**: Maximum 10 per function
- **Automated Validation**: Pre-commit hooks block violations

### Version Control & Collaboration

- **VCS**: Git
- **Branching Strategy**: GitHub Flow (feature branches → main)
- **Main Branch**: `main`
- **Commit Standards**: Conventional Commits (conventional prefixes)
- **Code Review Process**: Pull requests required for main branch
- **Protected Branches**: main branch requires reviews

### Dashboard Development

**Python TUI (Rich):**
- **Live Development**: Run via `./scripts/run.sh --tui`
- **Hot Reload**: Not applicable (terminal application)
- **Testing**: Manual testing in terminal environment
- **Debugging**: Rich console debugging features

**Rust CLI:**
- **Development Runs**: `cargo run -- --target <path> --output <path>`
- **Watch Mode**: `cargo watch` (optional dependency)
- **Fast Compilation**: Incremental compilation with sccache (optional)

## Deployment & Distribution

### Target Platform(s)
- **Operating Systems**: Linux, macOS, Windows
- **Architecture**: x86_64, aarch64 (Rust), any (Python)
- **Environment**: Local user machines (development, research, personal use)

### Distribution Method

**Rust Binary:**
- **Compilation**: Source distribution via Git
- **Installation**: Users compile with `cargo build --release`
- **Binary Location**: `target/release/text-extractor`
- **Future**: Potential binary releases via GitHub Releases

**Python Package:**
- **Installation Method**: Editable install (`pip install -e .`)
- **Script Entry Point**: `zlibrary-downloader` command (via pyproject.toml scripts)
- **Future**: PyPI distribution for `pip install zlibrary-downloader`

### Installation Requirements

**Rust Tool:**
- Rust toolchain (rustup) ≥1.70
- C compiler for some dependencies (pdf-extract)
- ~200MB disk space for dependencies

**Python Tool:**
- Python ≥3.8
- pip for package installation
- Virtual environment (recommended)
- ~50MB disk space for dependencies

**Shared:**
- Git for cloning repository
- ~500MB disk space for downloads and output

### Update Mechanism
- **Manual**: Users pull latest changes from Git and rebuild/reinstall
- **Future**: Version checking and update notifications

## Technical Requirements & Constraints

### Performance Requirements

**Text Extractor (Rust):**
- **Processing Speed**: <1 second per average-sized book (200-300 pages)
- **Memory Usage**: <100MB per process
- **Concurrency**: Single-threaded (planned: parallel processing)
- **Startup Time**: <100ms cold start

**Z-Library Downloader (Python):**
- **Search Response**: <3 seconds per search query
- **Download Speed**: Limited by network bandwidth and Z-Library servers
- **Memory Usage**: <150MB per process
- **TUI Responsiveness**: <100ms for user interactions

### Compatibility Requirements

**Platform Support:**
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch
- **macOS**: macOS 11+ (Big Sur and later)
- **Windows**: Windows 10/11 (via WSL or native)

**Rust Compatibility:**
- **Minimum Rust**: 1.70.0
- **Edition**: 2021
- **Standard Library**: std (not no_std)

**Python Compatibility:**
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Interpreter**: CPython (PyPy untested)

**Standards Compliance:**
- **PDF**: PDF 1.0-1.7 specifications
- **EPUB**: EPUB 2.0 and 3.0 standards
- **Text Encoding**: UTF-8 output

### Security & Compliance

**Credential Management:**
- **Storage**: `.env` file (not committed to version control)
- **Access Control**: File system permissions (user-only readable)
- **Transmission**: HTTPS for Z-Library API (TLS 1.2+)
- **No Logging**: Credentials never logged or printed

**Data Protection:**
- **User Data**: All processing local (no external data transmission except Z-Library)
- **Privacy**: No telemetry, analytics, or tracking
- **Book Files**: Stored locally, user responsible for legal compliance

**Threat Model:**
- **Credential Exposure**: Mitigated by .gitignore and environment variables
- **Man-in-the-Middle**: Mitigated by HTTPS enforcement
- **Malicious PDFs**: PDF parsing could be exploited (dependency risk)

**Compliance:**
- **Copyright**: Tool provided as-is, users responsible for legal use
- **Z-Library ToS**: Users must comply with Z-Library terms of service

### Scalability & Reliability

**Text Extractor:**
- **Expected Load**: 1-1000 files per batch
- **Concurrency**: Current: sequential, Future: rayon for parallel processing
- **Failure Handling**: Continue on error, report at end
- **Memory Scaling**: Linear with file size (processes one at a time)

**Z-Library Downloader:**
- **Expected Load**: 1-100 searches per session, 1-10 downloads per day
- **Rate Limiting**: Respects Z-Library daily quotas
- **Failure Handling**: Graceful error messages, no crash
- **Session Management**: Cookie-based session persistence

## Technical Decisions & Rationale

### Decision Log

1. **Rust for Text Extraction**:
   - **Rationale**: Performance, memory safety, strong type system, zero-cost abstractions
   - **Alternatives Considered**: Python (too slow), C++ (memory safety concerns)
   - **Trade-offs**: Steeper learning curve, longer compile times

2. **Python for Z-Library Integration**:
   - **Rationale**: Rich ecosystem for HTTP/API clients, existing Z-Library API wrapper, excellent TUI libraries
   - **Alternatives Considered**: Rust (less mature HTTP/TUI ecosystem in 2023)
   - **Trade-offs**: Slower performance (acceptable for I/O-bound API calls)

3. **Monorepo Structure**:
   - **Rationale**: Related tools, shared documentation, unified workflow, easy pipeline integration
   - **Alternatives Considered**: Separate repositories (harder to coordinate)
   - **Trade-offs**: Larger repo size, mixed language environments

4. **Cargo Workspaces (Rust)**:
   - **Rationale**: Shared dependencies, unified build, easy to add more Rust tools
   - **Alternatives Considered**: Single crate (less scalable)
   - **Trade-offs**: More complex Cargo.toml structure

5. **Rich Library for TUI**:
   - **Rationale**: Beautiful terminal UI, excellent documentation, active maintenance
   - **Alternatives Considered**: curses/urwid (steeper learning curve), textual (heavier)
   - **Trade-offs**: Dependency size (~13MB), terminal compatibility

6. **Environment Variables for Credentials**:
   - **Rationale**: Security best practice, prevents accidental commits, portable
   - **Alternatives Considered**: Config files (risk of commit), command-line args (visible in process list)
   - **Trade-offs**: Requires .env file setup

7. **Synchronous Processing**:
   - **Rationale**: Simpler implementation, sufficient for current use case
   - **Future Enhancement**: Async for parallel file processing
   - **Trade-offs**: Slower for large batches (acceptable for now)

8. **Pre-commit Quality Enforcement**:
   - **Rationale**: Enforce quality standards automatically, prevent bad commits
   - **Alternatives Considered**: CI-only checks (catches issues too late)
   - **Trade-offs**: Slower commit process, requires setup

## Known Limitations

1. **Sequential Processing (Text Extractor)**:
   - **Impact**: Slower for large batches of files
   - **Future Solution**: Implement parallel processing with rayon
   - **Timeline**: v0.2.0

2. **No OCR Support**:
   - **Impact**: Cannot extract text from image-based PDFs
   - **Future Solution**: Integrate tesseract OCR
   - **Timeline**: v0.3.0

3. **Limited Format Support**:
   - **Impact**: Only PDF and EPUB supported
   - **Future Solution**: Add MOBI, AZW3, DOCX support
   - **Timeline**: v0.2.0-v0.3.0

4. **No Progress Bar for Large Files**:
   - **Impact**: Users don't see progress during extraction of large files
   - **Future Solution**: Add indicatif progress bars
   - **Timeline**: v0.2.0

5. **Z-Library API Dependency**:
   - **Impact**: Tool breaks if Z-Library API changes
   - **Mitigation**: Monitor API changes, update wrapper
   - **Risk**: Medium (API relatively stable)

6. **No GUI**:
   - **Impact**: Terminal-only interface may be barrier for some users
   - **Future Solution**: Optional web-based GUI for monitoring
   - **Timeline**: v1.0.0+

7. **HTML Tag Stripping is Basic**:
   - **Impact**: EPUB extraction may have formatting artifacts
   - **Future Solution**: Use proper HTML parser (html5ever)
   - **Timeline**: v0.2.0

8. **No Configuration Files**:
   - **Impact**: Must specify arguments every time
   - **Future Solution**: Support .toml/.yaml config files
   - **Timeline**: v0.3.0

9. **Type Hints Incomplete (Python)**:
   - **Impact**: mypy cannot verify all code paths
   - **Action Required**: Add type hints throughout codebase
   - **Timeline**: v0.2.0 (required for QA compliance)

10. **Cyclomatic Complexity Violations**:
    - **Impact**: Some functions may exceed complexity limit of 10
    - **Action Required**: Refactor complex functions
    - **Audit**: Perform complexity audit on all existing code
    - **Timeline**: v0.2.0 (required for QA compliance)
