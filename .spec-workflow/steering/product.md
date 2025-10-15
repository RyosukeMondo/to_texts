# Product Overview

## Product Purpose
The `to_texts` project is a comprehensive monorepo containing tools for acquiring and processing ebooks. It solves two critical problems in the ebook workflow:

1. **Book Acquisition**: Provides an efficient, user-friendly interface to search and download books from Z-Library
2. **Text Extraction**: Extracts clean, formatted text from PDF and EPUB files for further processing, analysis, or conversion

The project enables researchers, students, developers, and book enthusiasts to build custom ebook workflows by combining these complementary tools.

## Target Users
**Primary Users:**
- **Researchers & Academics**: Need to extract text from academic papers and ebooks for analysis, citations, or research
- **Developers**: Building applications that process book content (NLP, machine learning, text analysis)
- **Book Enthusiasts**: Managing personal digital libraries and converting between formats
- **Students**: Accessing and processing educational materials efficiently

**User Needs & Pain Points:**
- Complicated interfaces for downloading books from Z-Library
- Difficulty extracting clean text from PDFs with proper encoding support
- No unified workflow for downloading and processing ebooks
- Manual, repetitive tasks when processing multiple files

## Key Features

1. **Z-Library Downloader (Python)**:
   - Beautiful interactive TUI (Text User Interface) with Rich library
   - Advanced search with multiple filters (format, year, language, author)
   - Command-line interface for automation and scripting
   - Secure credential management via environment variables
   - Both email/password and remix token authentication

2. **Text Extractor (Rust)**:
   - High-performance text extraction from PDF and EPUB files
   - Proper UTF-8 encoding support for international characters
   - Recursive directory processing for batch operations
   - Clean, formatted text output with metadata extraction
   - HTML tag stripping from EPUB content

3. **Unified Workflow**:
   - Monorepo structure for seamless integration
   - Download books → Extract text → Process/analyze pipeline
   - Consistent directory structure (downloads/ → tmp/)
   - Cross-language interoperability

## Business Objectives
- **Empower Users**: Provide professional-grade tools for ebook acquisition and processing
- **Maximize Efficiency**: Automate repetitive tasks in the ebook workflow
- **Ensure Quality**: Deliver clean, properly-encoded text extraction with high accuracy
- **Foster Integration**: Enable easy integration with existing workflows and tools
- **Maintain Simplicity**: Keep both tools simple, focused, and easy to use

## Success Metrics
- **Text Extraction Accuracy**: >95% successful extraction rate across PDF and EPUB formats
- **Processing Speed**: <1 second per average-sized book (Rust performance)
- **User Experience**: Zero-configuration setup with environment variables
- **Format Support**: PDF and EPUB with extensibility for additional formats
- **Error Handling**: Clear, actionable error messages for all failure cases

## Product Principles

1. **Separation of Concerns**: Each tool does one thing exceptionally well - downloading or extraction
2. **Performance Matters**: Use Rust for compute-intensive text extraction; Python for API integration
3. **User Choice**: Offer both interactive (TUI) and scriptable (CLI) interfaces
4. **Data Safety**: Never commit credentials; use environment variables and .gitignore
5. **Clean Output**: Prioritize readable, well-formatted text over raw extraction
6. **Fail Gracefully**: Handle errors without crashing; report progress clearly
7. **Quality First**: Enforce rigorous code quality standards through automated tooling and pre-commit verification

## Quality Assurance Standards

The project enforces comprehensive quality assurance across both Rust and Python codebases to ensure maintainability, reliability, and long-term sustainability.

### Design Principles

1. **SOLID Principles**:
   - **S**ingle Responsibility: Each module, class, and function has one clear purpose
   - **O**pen/Closed: Code is open for extension but closed for modification
   - **L**iskov Substitution: Subtypes must be substitutable for their base types
   - **I**nterface Segregation: Prefer small, focused interfaces over large, monolithic ones
   - **D**ependency Inversion: Depend on abstractions, not concretions

2. **SLAP (Single Level of Abstraction Principle)**: Functions operate at a single, consistent level of abstraction

3. **SSOT (Single Source of Truth)**: Each piece of data or logic has exactly one authoritative representation

4. **KISS (Keep It Simple, Stupid)**: Prefer simple, straightforward solutions over clever or complex ones

### Code Metrics & Limits

**File-level Constraints:**
- Maximum **400 lines per file** (excluding tests and generated code)
- Files exceeding this limit must be split into logical modules

**Function-level Constraints:**
- Maximum **30 lines per function**
- Functions exceeding this limit must be refactored into smaller, focused units

**Complexity Constraints:**
- Maximum **cyclomatic complexity of 10** per function
- Functions exceeding this must be simplified or decomposed

These limits apply to both **Rust** and **Python** codebases.

### Type Safety & Verification

**Compile-time Type Checking:**
- **Rust**: Leverage Rust's strong type system with zero-cost abstractions
- **Python**: Enforce type hints throughout the codebase, verified with `mypy`

**Pre-commit Verification:**
All commits must pass the following checks before being accepted:
- **Type checking**: `cargo check` (Rust), `mypy` (Python)
- **Linting**: `clippy` (Rust), `flake8` (Python)
- **Formatting**: `rustfmt` (Rust), `black` (Python)
- **Complexity analysis**: Verify cyclomatic complexity limits
- **Line count validation**: Ensure file and function size limits

**Quality Tools:**
- **Rust**: cargo clippy, cargo fmt, cargo test, cargo-complexity
- **Python**: mypy, black, flake8, pytest, radon (complexity)
- **Pre-commit**: Git hooks using `pre-commit` framework for automated validation

### Testing Standards
- **Unit tests**: Required for all business logic
- **Integration tests**: Required for file I/O and API interactions
- **Test coverage**: Target >80% code coverage
- **Property-based testing**: Use where appropriate (Rust: proptest, Python: hypothesis)

## Monitoring & Visibility

### Z-Library Downloader
- **Dashboard Type**: Terminal-based TUI with Rich library
- **Real-time Updates**: Progress spinners during search and download operations
- **Key Metrics Displayed**:
  - Search results with book metadata (title, author, year, format, language)
  - Downloads remaining quota
  - Download progress and file paths
- **Sharing Capabilities**: Command-line output can be piped/redirected for automation

### Text Extractor
- **Dashboard Type**: CLI with progress reporting
- **Real-time Updates**: File-by-file processing status
- **Key Metrics Displayed**:
  - Files processed successfully
  - Errors encountered
  - Output file paths
- **Sharing Capabilities**: Standard output for integration with scripts and pipelines

## Future Vision

### Potential Enhancements

**Short-term (v0.2.0):**
- **Format Support**: Add support for MOBI, AZW3, and DOC formats
- **Text Processing**: Add options for text cleaning (remove headers/footers, page numbers)
- **Metadata Extraction**: Export structured metadata (JSON/CSV) for cataloging

**Medium-term (v0.3.0):**
- **OCR Support**: Extract text from image-based PDFs using tesseract
- **Preview Mode**: Quick preview of extracted text before full processing
- **Batch Operations**: Improved batch download from Z-Library with queuing
- **Configuration Files**: Support for .toml/.yaml configuration for repeated workflows

**Long-term (v1.0.0+):**
- **Remote Access**: Web-based dashboard for monitoring extraction jobs
- **Analytics**: Track extraction quality metrics, processing time, format distribution
- **Collaboration**: Shared download queues and extraction job management
- **Cloud Integration**: S3/cloud storage upload for processed texts
- **API Server**: RESTful API for text extraction as a service
- **Database Integration**: Catalog books with full-text search capabilities
