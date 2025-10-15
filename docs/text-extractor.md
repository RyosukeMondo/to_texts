# Text Extractor Documentation

## Overview

The Text Extractor is a Rust-based CLI tool designed to extract clean, readable text from PDF and EPUB files. It handles complex encoding scenarios common in PDF files and provides clean output from EPUB documents.

## Architecture

### Project Structure

```
packages/rust/text-extractor/
├── Cargo.toml              # Package manifest
├── src/
│   └── main.rs             # Main application logic
└── README.md               # Project README
```

### Code Organization

The application is organized into several key functions:

- `main()` - Entry point, argument parsing, orchestration
- `extract_pdf_text()` - PDF text extraction logic
- `extract_epub_text()` - EPUB text extraction logic
- `strip_html_tags()` - HTML cleanup for EPUB content
- `generate_output_path()` - Output file path generation

## How It Works

### PDF Extraction

1. Opens PDF file using `pdf-extract` library
2. Library automatically handles:
   - Font encoding tables
   - Character mapping (CMap)
   - Unicode conversions
   - Embedded font data
3. Returns clean UTF-8 text
4. Writes to output file

**Key Advantage:** The `pdf-extract` library handles complex PDF internals that manual parsing would struggle with.

### EPUB Extraction

1. Opens EPUB file using `epub` library
2. Extracts metadata (title, author)
3. Iterates through all HTML/XHTML resources
4. Strips HTML tags while preserving text
5. Assembles clean text output
6. Writes to output file

## Usage Patterns

### Single File Processing

```bash
text-extractor --target ./book.pdf --output ./extracted/
```

Output: `./extracted/book.txt`

### Batch Processing

```bash
text-extractor --target ./library/ --output ./extracted/
```

Processes all PDFs and EPUBs in `./library/` recursively.

### Integration with Z-Library Downloader

```bash
# Download books
cd packages/python/zlibrary-downloader
./scripts/run.sh --title "Machine Learning" --format pdf --download

# Extract text
cd ../../rust
cargo run --release -- --target ../../../downloads/ --output ../../../tmp/
```

## Error Handling

The tool provides graceful error handling:

- **File Not Found** - Clear error message with path
- **Invalid PDF/EPUB** - Logs error, continues processing other files
- **Permission Errors** - Reports and skips
- **Corrupt Files** - Logs warning, continues

Example output:
```
Processing PDF: /path/to/book.pdf
  -> Error: Failed to extract text from PDF: Invalid file format
  -> Continuing with next file...
```

## Performance Considerations

### Rust Benefits

- **Fast** - Compiled binary with zero-cost abstractions
- **Safe** - Memory safety without garbage collection
- **Efficient** - Minimal overhead for file I/O

### Optimization Tips

1. **Use Release Mode** - `cargo build --release` for 10-100x speedup
2. **SSD Storage** - I/O bound operations benefit from fast storage
3. **Batch Processing** - Process large directories in single invocation

### Benchmarks

Approximate performance (release build, modern hardware):

- Small PDF (10 pages): ~50ms
- Medium PDF (100 pages): ~200ms
- Large PDF (500 pages): ~1s
- EPUB (novel): ~100ms

## Limitations

### Current Limitations

1. **Image-based PDFs** - Cannot extract text from scanned documents (requires OCR)
2. **DRM-protected EPUBs** - Cannot read encrypted files
3. **Complex PDF layouts** - Multi-column layouts may have text order issues
4. **No OCR support** - Pure text extraction only

### Future Enhancements

- [ ] Parallel processing for batch operations
- [ ] OCR support for image-based PDFs
- [ ] Better layout preservation
- [ ] Progress bars for large batches
- [ ] Format detection and validation
- [ ] Configurable output formatting

## Troubleshooting

### Issue: Garbled Text Output

**Symptoms:** Output contains symbols, control characters, or unreadable text

**Causes:**
- Custom font encodings (rare, but possible even with pdf-extract)
- Image-based PDF (no embedded text)
- Corrupt PDF file

**Solutions:**
1. Try a different PDF viewer to verify the PDF has text
2. Check if PDF is image-based (needs OCR)
3. Try re-downloading or obtaining a different version

### Issue: Empty Output Files

**Symptoms:** Output files created but contain no text

**Causes:**
- Image-only PDF (scanned document)
- Empty EPUB content
- Unsupported DRM

**Solutions:**
1. Verify source file has actual text content
2. Check file is not DRM-protected
3. Try opening in native reader to verify

### Issue: Build Errors

**Symptoms:** `cargo build` fails

**Solutions:**
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
cargo build --release

# Check Cargo.toml is valid
cargo check
```

## API Reference

### Command Line Interface

```
text-extractor --target <PATH> --output <PATH>
```

**Arguments:**

- `--target, -t <PATH>`
  - Target path to search for PDF/EPUB files
  - Can be file or directory
  - Required

- `--output, -o <PATH>`
  - Output directory for extracted text
  - Created if doesn't exist
  - Required

### Exit Codes

- `0` - Success (all files processed)
- `1` - Error (invalid arguments or critical failure)

## Contributing

### Development Setup

```bash
cd packages/rust/text-extractor

# Install dependencies
cargo fetch

# Run in debug mode
cargo run -- --target test_files/ --output output/

# Run tests
cargo test

# Check code
cargo clippy
cargo fmt --check
```

### Adding New Formats

To add support for new document formats:

1. Add crate dependency in `Cargo.toml`
2. Create new extraction function (e.g., `extract_docx_text()`)
3. Add format detection in `main()` loop
4. Update documentation

Example:
```rust
fn extract_docx_text(path: &Path, output_dir: &Path) -> Result<PathBuf> {
    // Implementation here
}
```

## Related Documentation

- [Main README](../../../README.md)
- [Z-Library Downloader Documentation](./zlibrary-downloader.md)
- [Rust Text Extractor README](../packages/rust/text-extractor/README.md)
