# Z-Library Downloader Documentation

## Overview

The Z-Library Downloader is a Python-based tool providing multiple interfaces (TUI, CLI, Interactive) for searching and downloading books from Z-Library. It features a beautiful text-based user interface powered by the `rich` library.

## Architecture

### Project Structure

```
packages/python/zlibrary-downloader/
├── zlibrary_downloader/        # Main package
│   ├── __init__.py             # Package exports
│   ├── client.py               # Z-Library API wrapper
│   ├── cli.py                  # Command-line interface
│   └── tui.py                  # Text User Interface
├── scripts/
│   ├── setup.sh                # Setup script
│   └── run.sh                  # Run script
├── requirements.txt            # Dependencies
├── pyproject.toml             # Modern Python packaging
└── README.md                  # Project README
```

### Module Organization

**client.py** - Z-Library API Client
- Handles authentication (email/password or remix tokens)
- Makes API requests to Z-Library endpoints
- Manages cookies and sessions
- Book search and download operations

**cli.py** - Command-Line Interface
- Argument parsing with `argparse`
- Three modes: direct CLI, classic interactive, TUI
- Credential loading from environment
- Orchestrates search and download operations

**tui.py** - Text User Interface
- Rich interactive interface with colors and formatting
- Interactive prompts with validation
- Beautiful tables for search results
- Progress indicators for operations

## Setup and Configuration

### Installation

```bash
cd packages/python/zlibrary-downloader

# Run setup script
./scripts/setup.sh

# This will:
# - Create virtual environment
# - Install dependencies
# - Install package in editable mode
```

### Configuration

Credentials are stored in `.env` at the repository root:

```bash
# Copy example
cp .env.example .env

# Edit with your credentials
nano .env
```

**Method 1: Remix Credentials (Recommended)**
```env
ZLIBRARY_REMIX_USERID=123456
ZLIBRARY_REMIX_USERKEY=abc123def456
```

Get these from browser cookies after logging into Z-Library:
1. Open browser DevTools (F12)
2. Go to Application → Cookies
3. Find `remix_userid` and `remix_userkey`
4. Copy values to `.env`

**Method 2: Email/Password**
```env
ZLIBRARY_EMAIL=your_email@example.com
ZLIBRARY_PASSWORD=your_password
```

## Usage Modes

### 1. TUI Mode (Recommended)

Beautiful interactive interface with rich formatting.

```bash
./scripts/run.sh --tui
```

**Features:**
- Interactive prompts with validation
- Colorful tables and panels
- Toggle options for filters
- Progress indicators
- Error handling with friendly messages

**Workflow:**
1. Enter search query (required)
2. Optional: Filter by format (pdf, epub, etc.)
3. Optional: Filter by year range
4. Optional: Filter by language
5. Optional: Sort order
6. Optional: Limit results
7. Confirm search
8. View results in formatted table
9. Download selected book

### 2. Command-Line Mode

Direct search and optional download.

```bash
# Search only
./scripts/run.sh --title "Python Programming"

# Search and download
./scripts/run.sh --title "Python Programming" --download

# Advanced search
./scripts/run.sh --title "Machine Learning" \
  --format pdf \
  --year-from 2020 \
  --language english \
  --limit 10 \
  --download
```

### 3. Classic Interactive Mode

Simple text-based menu.

```bash
./scripts/run.sh --classic
```

Menu options:
1. Search for books
2. Get most popular books
3. Get profile information
4. Exit

## Search Filters

### File Formats

Common formats: `pdf`, `epub`, `mobi`, `azw3`, `fb2`, `txt`, `djvu`, `doc`, `docx`, `rtf`

```bash
./scripts/run.sh --title "Book Title" --format epub
```

### Year Range

Filter by publication year:

```bash
./scripts/run.sh --title "AI" --year-from 2020 --year-to 2024
```

### Language

Available languages: `english`, `spanish`, `french`, `german`, `russian`, `italian`, `portuguese`, `chinese`, `japanese`, `korean`, `arabic`

```bash
./scripts/run.sh --title "Programming" --language english
```

### Sort Order

- `popular` - Most popular books first
- `year` - Newest books first
- `title` - Alphabetical by title

```bash
./scripts/run.sh --title "Science" --order year
```

### Pagination

```bash
./scripts/run.sh --title "History" --limit 20 --page 2
```

## API Reference

### Client Class (client.py)

```python
from zlibrary_downloader import Zlibrary

# Initialize with remix credentials
client = Zlibrary(
    remix_userid="123456",
    remix_userkey="abc123"
)

# Or with email/password
client = Zlibrary(
    email="user@example.com",
    password="password"
)

# Search books
results = client.search(
    message="Python",
    extensions="pdf",
    yearFrom=2020,
    yearTo=2024,
    languages="english",
    order="popular",
    limit=10
)

# Download book
filename, content = client.downloadBook(results['books'][0])
with open(filename, 'wb') as f:
    f.write(content)
```

### Key Methods

**Authentication:**
- `login(email, password)` - Login with credentials
- `loginWithToken(remix_userid, remix_userkey)` - Login with tokens
- `isLoggedIn()` - Check login status

**Search:**
- `search(message, yearFrom, yearTo, languages, extensions, order, page, limit)` - Search books
- `getMostPopular(switch_language)` - Get popular books
- `getRecently()` - Get recent books

**Profile:**
- `getProfile()` - Get user profile
- `getDownloadsLeft()` - Check remaining downloads

**Download:**
- `downloadBook(book)` - Download book, returns (filename, content)
- `getImage(book)` - Download book cover

## Error Handling

### Common Errors

**Invalid Credentials**
```
Error: No valid credentials found in .env file
```
Solution: Check `.env` file exists and contains valid credentials

**Login Failed**
```
Error: Login unsuccessful
```
Solution: Verify credentials are correct, try remix tokens instead

**Download Limit Reached**
```
Error: Daily download limit reached
```
Solution: Wait 24 hours or upgrade Z-Library account

**Network Errors**
```
Error during search: Connection timeout
```
Solution: Check internet connection, Z-Library may be down

### Debug Mode

For detailed error information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

### Optimization Tips

1. **Use Remix Tokens** - Faster authentication
2. **Limit Results** - Reduce API response time
3. **Cache Searches** - Store results for later review
4. **Batch Downloads** - Download multiple books in one session

### Rate Limiting

Z-Library has rate limits:
- **Search**: ~100 requests/hour
- **Downloads**: Account-dependent (typically 10/day for free accounts)

Respect rate limits to avoid IP bans.

## Troubleshooting

### Issue: TUI Not Available

**Symptoms:** Falls back to classic mode or error about 'rich'

**Solution:**
```bash
pip install rich>=13.7.0
```

### Issue: Module Not Found

**Symptoms:** `ModuleNotFoundError: No module named 'zlibrary_downloader'`

**Solution:**
```bash
cd packages/python/zlibrary-downloader
pip install -e .
```

### Issue: Environment Variables Not Loading

**Symptoms:** "No valid credentials found"

**Solution:**
- Verify `.env` exists at repository root
- Check `.env` syntax (no quotes needed)
- Ensure `python-dotenv` is installed

### Issue: Downloads Failing

**Symptoms:** Book search works but download fails

**Possible Causes:**
1. Daily download limit reached
2. Invalid book entry
3. Network issues

**Debug:**
```python
# Check downloads left
profile = client.getProfile()
print(f"Downloads today: {profile['user']['downloads_today']}")
print(f"Limit: {profile['user']['downloads_limit']}")
```

## Security Considerations

### Credential Storage

- Never commit `.env` to version control (already in `.gitignore`)
- Use remix tokens instead of password when possible
- Consider using environment variables for CI/CD

### Legal Considerations

⚠️ **Important:** Z-Library operates in a legal gray area in many jurisdictions. This tool is for educational purposes. Users are responsible for ensuring compliance with local copyright laws.

**Guidelines:**
- Only download books you have the right to access
- Respect copyright laws in your jurisdiction
- Use for personal, non-commercial purposes
- Consider purchasing books to support authors

## Development

### Running Tests

```bash
cd packages/python/zlibrary-downloader

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=zlibrary_downloader
```

### Code Quality

```bash
# Format code
black zlibrary_downloader/

# Lint
flake8 zlibrary_downloader/

# Type checking
mypy zlibrary_downloader/
```

### Adding New Features

**Example: Adding a new search filter**

1. Update `search()` parameters in `client.py`
2. Add argument to CLI parser in `cli.py`
3. Add interactive prompt in TUI mode in `tui.py`
4. Update documentation

## Integration Examples

### Integration with Text Extractor

Download and extract workflow:

```bash
# 1. Download books
cd packages/python/zlibrary-downloader
./scripts/run.sh --title "Data Science" --format pdf --download

# 2. Extract text
cd ../../rust
cargo run --release -- \
  --target ../../../downloads/ \
  --output ../../../tmp/

# 3. Process extracted text
cat ../../../tmp/*.txt | grep "machine learning"
```

### Automation Script

```bash
#!/bin/bash
# download_and_extract.sh

QUERY="$1"
FORMAT="${2:-pdf}"

cd packages/python/zlibrary-downloader
./scripts/run.sh --title "$QUERY" --format "$FORMAT" --download

cd ../../rust
cargo run --release -- --target ../../../downloads/ --output ../../../tmp/

echo "Text extracted to tmp/"
```

Usage:
```bash
./download_and_extract.sh "Python Programming" pdf
```

## Related Documentation

- [Main README](../../../README.md)
- [Text Extractor Documentation](./text-extractor.md)
- [Z-Library Downloader README](../packages/python/zlibrary-downloader/README.md)
- [Z-Library API GitHub](https://github.com/bipinkrish/Zlibrary-API)
