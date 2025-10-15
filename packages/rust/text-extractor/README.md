# Text Extractor

A high-performance Rust CLI tool for extracting text from PDF and EPUB files with proper encoding support.

## Features

- **PDF Text Extraction** - Properly handles PDF character encodings, font mappings, and Unicode conversions
- **EPUB Text Extraction** - Extracts clean text from EPUB files with HTML tag stripping
- **Recursive Processing** - Walk through directories to process multiple files
- **Multiple Output Formats** - Save extracted text to organized output files
- **Error Handling** - Graceful error handling with detailed error messages

## Installation

### From Source

```bash
# Navigate to this directory
cd packages/rust/text-extractor

# Build in release mode for best performance
cargo build --release

# Binary will be at target/release/text-extractor
```

## Usage

### Basic Usage

```bash
# Extract text from a single file
text-extractor --target /path/to/file.pdf --output ./extracted/

# Extract text from all PDFs and EPUBs in a directory
text-extractor --target /path/to/books/ --output ./extracted/
```

### Examples

```bash
# Process downloaded books
text-extractor --target ../../../downloads/ --output ../../../tmp/

# Process with specific directory structure
text-extractor --target ~/Documents/Books --output ~/Documents/ExtractedText
```

## Command Line Options

- `--target, -t` - Target path to search recursively for PDF or EPUB files (required)
- `--output, -o` - Output path to save extracted texts (required)

## Supported Formats

- **PDF** - Portable Document Format (`.pdf`)
- **EPUB** - Electronic Publication (`.epub`)

## Technical Details

### PDF Extraction
Uses the `pdf-extract` library which properly handles:
- Custom font encodings
- Character mapping (CMap) tables
- Unicode conversions
- Embedded fonts

### EPUB Extraction
- Parses EPUB metadata (title, author)
- Extracts HTML/XHTML content
- Strips HTML tags for clean text output
- Preserves document structure

## Performance

Built with Rust for:
- **Speed** - Fast processing of large document collections
- **Memory Safety** - No segfaults or memory leaks
- **Concurrency** - Potential for parallel processing (future enhancement)

## Troubleshooting

### PDF Text is Garbled
This usually indicates encoding issues. This tool uses `pdf-extract` which should handle most encodings correctly. If you still encounter issues:
- Check if the PDF is image-based (requires OCR, not supported)
- Some PDFs with custom fonts may not extract perfectly

### EPUB Not Extracting
- Ensure the file is a valid EPUB (ZIP format with specific structure)
- Some DRM-protected EPUBs cannot be read

## Development

### Running Tests
```bash
cargo test
```

### Linting
```bash
cargo clippy
```

### Formatting
```bash
cargo fmt
```

## Dependencies

- `clap` - Command-line argument parsing
- `pdf-extract` - PDF text extraction with encoding support
- `epub` - EPUB file parsing
- `walkdir` - Recursive directory traversal
- `anyhow` - Error handling

## License

MIT OR Apache-2.0
