# Z-Library Book Downloader

A Python tool to programmatically search and download books from Z-Library using credentials stored in a `.env` file.

## Setup

### 1. Run Setup Script

```bash
./setup.sh
```

This will:
- Create a virtual environment (if it doesn't exist)
- Install all required dependencies

### 2. Configure Credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Z-Library credentials. You have two options:

#### Option A: Remix Credentials (Recommended)

1. Log in to Z-Library in your browser
2. Open browser developer tools (F12)
3. Go to Application/Storage → Cookies
4. Find `remix_userid` and `remix_userkey` cookies
5. Copy their values to your `.env` file:

```env
ZLIBRARY_REMIX_USERID=your_remix_userid_here
ZLIBRARY_REMIX_USERKEY=your_remix_userkey_here
```

#### Option B: Email and Password

```env
ZLIBRARY_EMAIL=your_email@example.com
ZLIBRARY_PASSWORD=your_password
```

## Usage

### TUI Mode (Recommended)

Launch the beautiful interactive TUI (Text User Interface) mode:

```bash
./run.sh --tui
```

Or simply run without arguments (TUI is the default):

```bash
./run.sh
```

The TUI mode features:
- Rich, colorful interface with tables and panels
- Interactive prompts for all search options
- Input validation with min/max guards
- Toggle options for filters
- Progress indicators for searches and downloads
- Beautiful result display in formatted tables

### Classic Interactive Mode

For a simple text-based menu interface:

```bash
./run.sh --classic
```

This provides a basic menu with options to:
1. Search for books
2. Get most popular books
3. View profile information
4. Exit

### Command Line Mode

**Search only** (displays results without downloading):

```bash
./run.sh --title "The Great Gatsby"
```

**Search and download** the first result:

```bash
./run.sh --title "The Great Gatsby" --download
```

### Advanced Search Options

The tool supports comprehensive search filters:

#### Available Arguments

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--title` | string | Book title or search query (required for CLI mode) | `--title "Python Programming"` |
| `--download` | flag | Download the first search result | `--download` |
| `--format` | string | File format filter | `--format pdf` |
| `--year-from` | integer | Filter books published from this year | `--year-from 2020` |
| `--year-to` | integer | Filter books published until this year | `--year-to 2024` |
| `--language` | string | Filter by language | `--language english` |
| `--order` | string | Sort order (popular, year, title) | `--order year` |
| `--limit` | integer | Maximum number of results | `--limit 10` |
| `--page` | integer | Page number for pagination | `--page 2` |

#### Supported Formats

Common formats: `pdf`, `epub`, `mobi`, `azw3`, `fb2`, `txt`, `djvu`, `doc`, `docx`, `rtf`, `zip`, `rar`

#### Supported Languages

Common languages: `english`, `spanish`, `french`, `german`, `russian`, `italian`, `portuguese`, `chinese`, `japanese`, `korean`, etc.

#### Sort Orders

- `popular` - Most popular books first
- `year` - Newest books first
- `title` - Alphabetical by title

### Usage Examples

**Search for PDF books only:**
```bash
./run.sh --title "Machine Learning" --format pdf
```

**Search and download recent books:**
```bash
./run.sh --title "Python Programming" --year-from 2022 --download
```

**Search with multiple filters:**
```bash
./run.sh --title "Data Science" --format epub --language english --year-from 2020 --year-to 2024 --limit 5
```

**Search and sort by popularity:**
```bash
./run.sh --title "Artificial Intelligence" --order popular --format pdf --download
```

**Paginated search:**
```bash
./run.sh --title "Web Development" --limit 20 --page 1
```

### Get Help

To see all available options:
```bash
./run.sh --help
```

## Features

### TUI Features (with rich library)
- **Beautiful interface** with colors, tables, and formatted panels
- **Interactive prompts** with validation and defaults
- **Min/Max guards** for year ranges (1800-2100) and result limits (1-100)
- **Toggle prompts** for optional filters (yes/no questions)
- **Choice menus** for formats, languages, and sort orders
- **Progress indicators** for searches and downloads
- **Rich tables** for displaying search results
- **Error handling** with friendly messages

### General Features
- **Search books** by title, author, or keywords
- **Advanced filters** - Format, year range, language, sort order
- **Download books** in various formats (PDF, EPUB, MOBI, etc.)
- **View most popular books**
- **Check profile information**
- **Pagination support** for browsing large result sets
- **Automatic downloads directory** (created as `downloads/`)
- **Multiple modes** - TUI, Classic Interactive, or Command-line
- **Comprehensive help** with `--help` flag

## File Structure

```
.
├── setup.sh                 # Setup script (creates venv, installs dependencies)
├── run.sh                   # Run script (activates venv and runs downloader)
├── Zlibrary.py              # Z-Library API wrapper
├── zlibrary_downloader.py   # Main downloader script
├── zlibrary_tui.py          # TUI module (rich interface)
├── requirements.txt         # Python dependencies (includes rich)
├── .env.example            # Template for credentials
├── .env                    # Your actual credentials (gitignored)
├── venv/                   # Virtual environment (created by setup.sh)
└── downloads/              # Downloaded books (created automatically)
```

## Legal Notice

This tool is for educational purposes. Z-Library operates in a legal gray area in many jurisdictions. Users are responsible for ensuring their use complies with local copyright laws. Only download books you have the right to access.

## Credits

Uses the unofficial Z-Library API wrapper by [bipinkrish](https://github.com/bipinkrish/Zlibrary-API)
