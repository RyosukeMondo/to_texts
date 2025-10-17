#!/usr/bin/env python3
"""
Z-Library Book Downloader
Search and download books from Z-Library using credentials from configuration file
Supports both TOML (multiple credentials) and .env (single credential) formats
"""

import os
import sys
import argparse
import logging
from typing import Optional, Any, List, Dict
from .client import Zlibrary
from .credential_manager import CredentialManager
from .client_pool import ZlibraryClientPool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import TUI module (optional)
try:
    from .tui import ZLibraryTUI

    TUI_AVAILABLE = True
except ImportError:
    TUI_AVAILABLE = False


def load_credentials() -> tuple[CredentialManager, ZlibraryClientPool]:
    """
    Load credentials and initialize credential manager and client pool.

    Supports both TOML (zlibrary_credentials.toml) and .env formats.
    TOML format allows multiple credentials with automatic rotation.
    .env format provides backward compatibility with single credential.

    Returns:
        tuple[CredentialManager, ZlibraryClientPool]: Initialized manager and pool

    Raises:
        SystemExit: If no credentials found or loading fails
    """
    try:
        credential_manager = CredentialManager()
        credential_manager.load_credentials()
        client_pool = ZlibraryClientPool(credential_manager)
        return credential_manager, client_pool
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease create one of the following:")
        print("  1. zlibrary_credentials.toml (recommended for multiple accounts)")
        print("  2. .env (single account, backward compatible)")
        sys.exit(1)
    except ValueError as e:
        print(f"Error loading credentials: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error loading credentials: {e}")
        sys.exit(1)


def initialize_zlibrary(client_pool: ZlibraryClientPool) -> Zlibrary:
    """
    Initialize Z-Library client from client pool.

    Args:
        client_pool: ZlibraryClientPool instance

    Returns:
        Zlibrary: Authenticated Z-Library client

    Raises:
        SystemExit: If client initialization fails
    """
    client = client_pool.get_current_client()

    if client is None:
        print("Error: Failed to initialize Z-Library client")
        print("Please check your credentials and try again")
        sys.exit(1)

    return client


def display_credential_status(credential_manager: CredentialManager) -> None:
    """
    Display summary of loaded credentials and their status.

    Shows:
    - Total number of credentials loaded
    - Currently active credential
    - Available vs exhausted credentials
    - Download limits (if available)

    Args:
        credential_manager: CredentialManager instance
    """
    print("\n" + "=" * 60)
    print("Credential Status")
    print("=" * 60)

    total_creds = len(credential_manager.credentials)
    available_creds = len(credential_manager.get_available())
    current_cred = credential_manager.get_current()

    print(f"Total credentials: {total_creds}")
    print(f"Available credentials: {available_creds}")

    if current_cred:
        print(f"Current credential: {current_cred.identifier}")

        # Display authentication method
        if current_cred.remix_userid and current_cred.remix_userkey:
            auth_method = "Remix tokens"
        elif current_cred.email and current_cred.password:
            auth_method = "Email/password"
        else:
            auth_method = "Unknown"
        print(f"Authentication: {auth_method}")

        # Display download limits if available
        if current_cred.downloads_left is not None:
            print(f"Downloads remaining: {current_cred.downloads_left}")

    print("=" * 60)


def _build_search_params(query: str, **kwargs: Any) -> Dict[str, Any]:
    """Build search parameters dictionary from query and kwargs."""
    search_params: Dict[str, Any] = {"message": query}

    # Map of kwargs to search parameter names
    param_mapping = {
        "format": "extensions",
        "year_from": "yearFrom",
        "year_to": "yearTo",
        "language": "languages",
        "order": "order",
        "limit": "limit",
        "page": "page",
    }

    # Add optional parameters if provided
    for kwarg_name, param_name in param_mapping.items():
        if kwargs.get(kwarg_name):
            search_params[param_name] = kwargs[kwarg_name]

    return search_params


def _check_download_limit_warning(credential_manager: CredentialManager) -> None:
    """Check and warn if current credential is approaching download limits."""
    current_cred = credential_manager.get_current()
    if not current_cred or current_cred.downloads_left is None:
        return

    # Warn if downloads left is 5 or less (but not 0)
    if 0 < current_cred.downloads_left <= 5:
        print(
            f"\n⚠️  Warning: Only {current_cred.downloads_left} download(s) remaining "
            f"for credential '{current_cred.identifier}'"
        )
        logger.warning(
            f"Credential '{current_cred.identifier}' approaching limit: "
            f"{current_cred.downloads_left} downloads remaining"
        )


def _rotate_after_operation(client_pool: ZlibraryClientPool, operation: str) -> None:
    """Rotate to next credential after successful operation."""
    current_cred = client_pool.credential_manager.get_current()
    if current_cred:
        logger.info(f"{operation} successful with credential: {current_cred.identifier}")

    next_cred = client_pool.credential_manager.rotate()
    if next_cred:
        logger.info(f"Rotated to next credential: {next_cred.identifier}")
    else:
        logger.warning("All credentials exhausted - cannot rotate")


def _handle_operation_failure(
    client_pool: Optional[ZlibraryClientPool],
    attempt: int,
    max_retries: int,
    cred_id: str,
    operation: str,
) -> bool:
    """Handle operation failure and determine if retry should occur."""
    if not client_pool or attempt >= max_retries - 1:
        return False

    available_creds = client_pool.credential_manager.get_available()
    if len(available_creds) > 1:
        print(f"⚠️  {operation} failed with '{cred_id}'. Trying next credential...")
        logger.info(f"Rotating to next credential after {operation.lower()} failure")
        client_pool.credential_manager.rotate()
        return True

    print("❌ Error: All credentials exhausted or unavailable")
    logger.error("No more credentials available for retry")
    return False


def search_books(
    z_client: Zlibrary,
    query: str,
    client_pool: Optional[ZlibraryClientPool] = None,
    save_to_db: bool = False,
    search_service: Any = None,
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """
    Search for books on Z-Library with optional filters.

    Automatically rotates to next credential after successful search when
    using multi-credential setup. Implements retry logic with next credential
    on failures. Optionally stores results in database.

    Args:
        z_client: Z-Library client to use for search
        query: Search query string
        client_pool: Optional client pool for credential rotation
        save_to_db: Whether to save results to database (default: False)
        search_service: SearchService instance for database storage
        **kwargs: Additional search parameters (format, year_from, year_to, etc.)

    Returns:
        Optional[Dict[str, Any]]: Search results or None if search failed
    """
    print(f"\nSearching for: {query}")

    search_params = _build_search_params(query, **kwargs)
    max_retries = 3 if client_pool else 1
    last_error = None

    for attempt in range(max_retries):
        try:
            # Use current client from pool
            current_client = (
                z_client
                if attempt == 0
                else (client_pool.get_current_client() if client_pool else z_client)
            )

            if not current_client:
                logger.error("No available client for search")
                break

            # If save_to_db is enabled, use SearchService
            if save_to_db and search_service:
                try:
                    # SearchService returns List[Book], convert back to API format
                    stored_books = search_service.search_and_store(
                        current_client, query, **search_params
                    )
                    # Still perform normal search to get full API response
                    results = current_client.search(**search_params)
                    if results:
                        print(f"✓ Stored {len(stored_books)} books in database")
                except Exception as db_error:
                    # Database errors shouldn't break search
                    logger.warning(f"Database storage failed: {db_error}")
                    print(f"⚠️  Warning: Could not save to database: {db_error}")
                    # Continue with normal search
                    results = current_client.search(**search_params)
            else:
                results = current_client.search(**search_params)

            # Rotate to next credential after successful search
            if results and client_pool:
                _rotate_after_operation(client_pool, "Search")

            return results

        except Exception as e:
            last_error = e
            current_cred = client_pool.credential_manager.get_current() if client_pool else None
            cred_id = current_cred.identifier if current_cred else "unknown"

            logger.error(f"Search attempt {attempt + 1} failed with credential '{cred_id}': {e}")

            # Try next credential if available
            if not _handle_operation_failure(client_pool, attempt, max_retries, cred_id, "Search"):
                break

    # All retries exhausted
    if last_error:
        print(f"❌ Error searching: {last_error}")
        logger.error(f"Search failed after {max_retries} attempts: {last_error}")

    return None


def display_results(results: Optional[Dict[str, Any]]) -> None:
    """Display search results"""
    if not results or "books" not in results:
        print("No results found")
        return

    books = results["books"]
    print(f"\nFound {len(books)} books:\n")

    for idx, book in enumerate(books, 1):
        print(f"{idx}. {book.get('title', 'N/A')}")
        print(f"   Author: {book.get('author', 'N/A')}")
        print(f"   Year: {book.get('year', 'N/A')}")
        print(f"   Publisher: {book.get('publisher', 'N/A')}")
        print(f"   Language: {book.get('language', 'N/A')}")
        print(f"   Extension: {book.get('extension', 'N/A')}")
        print(f"   Size: {book.get('size', 'N/A')}")
        print()


def _update_download_limits(client_pool: ZlibraryClientPool) -> None:
    """Update download limits for current credential and log results."""
    current_cred = client_pool.credential_manager.get_current()
    if not current_cred:
        return

    logger.info(f"Download successful with credential: {current_cred.identifier}")

    success, error = client_pool.credential_manager.update_downloads_left(current_cred)
    if success and current_cred.downloads_left is not None:
        logger.info(
            f"Downloads remaining for {current_cred.identifier}: " f"{current_cred.downloads_left}"
        )
        print(f"Downloads remaining: {current_cred.downloads_left}")
    elif error:
        logger.warning(f"Could not update download limits: {error}")


def _rotate_after_download(client_pool: ZlibraryClientPool) -> None:
    """Rotate to next credential after download."""
    next_cred = client_pool.credential_manager.rotate()
    if next_cred:
        logger.info(f"Rotated to next credential: {next_cred.identifier}")
    else:
        logger.warning("All credentials exhausted - cannot rotate")
        print("\nWarning: All credentials exhausted. No more downloads available.")


def _check_and_skip_exhausted_credential(
    client_pool: ZlibraryClientPool,
) -> bool:
    """Check if current credential is exhausted and skip if needed."""
    current_cred = client_pool.credential_manager.get_current()
    if (
        current_cred
        and current_cred.downloads_left is not None
        and current_cred.downloads_left == 0
    ):
        logger.warning(
            f"Credential '{current_cred.identifier}' has 0 downloads left, rotating to next"
        )
        available_creds = client_pool.credential_manager.get_available()
        if not available_creds:
            print("❌ Error: All credentials have reached their download limits")
            logger.error("All credentials exhausted - cannot download")
            return False
        client_pool.credential_manager.rotate()
    return True


def _perform_download(client: Zlibrary, book: Dict[str, Any], download_dir: str) -> Optional[str]:
    """Perform the actual download and file save operation."""
    print(f"Downloading: {book.get('title', 'Unknown')}")
    download_result = client.downloadBook(book)

    if download_result is None:
        raise RuntimeError("Download failed (no content returned)")

    filename, filecontent = download_result

    # Save the file
    filepath = os.path.join(download_dir, filename)
    with open(filepath, "wb") as bookfile:
        bookfile.write(filecontent)

    print(f"✓ Successfully downloaded to: {filepath}")
    return filepath


def download_book(
    z_client: Zlibrary,
    book: Dict[str, Any],
    client_pool: Optional[ZlibraryClientPool] = None,
    download_dir: str = "downloads",
    download_service: Any = None,
) -> Optional[str]:
    """
    Download a book from Z-Library.

    Automatically rotates to next credential and updates download limits
    after successful download when using multi-credential setup. Implements
    retry logic with next credential on failures. Optionally records
    download to database.

    Args:
        z_client: Z-Library client to use for download
        book: Book metadata dictionary
        client_pool: Optional client pool for credential rotation
        download_dir: Directory to save downloaded books
        download_service: Optional DownloadService for tracking

    Returns:
        Optional[str]: Path to downloaded file or None if download failed
    """
    # Create downloads directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    # Check for download limit warnings before attempting
    if client_pool:
        _check_download_limit_warning(client_pool.credential_manager)

    max_retries = 3 if client_pool else 1
    last_error = None

    for attempt in range(max_retries):
        try:
            # Check if current credential has exhausted downloads
            if client_pool and not _check_and_skip_exhausted_credential(client_pool):
                return None

            # Use current client from pool
            current_client = (
                z_client
                if attempt == 0
                else (client_pool.get_current_client() if client_pool else z_client)
            )

            if not current_client:
                logger.error("No available client for download")
                print("❌ Error: No available credentials for download")
                return None

            filepath = _perform_download(current_client, book, download_dir)

            # Record download in database if service available
            if download_service:
                try:
                    credential_id = (
                        client_pool.credential_manager.get_current().id
                        if client_pool and client_pool.credential_manager.get_current()
                        else None
                    )
                    download_service.record_download(
                        book_id=str(book.get("id", "")),
                        credential_id=credential_id,
                        filename=os.path.basename(filepath),
                        path=filepath,
                        size=os.path.getsize(filepath),
                    )
                except Exception as db_error:
                    logger.warning(f"Failed to record download in database: {db_error}")

            # Update download limits and rotate after successful download
            if client_pool:
                _update_download_limits(client_pool)
                _rotate_after_download(client_pool)

            return filepath

        except Exception as e:
            last_error = e
            current_cred = client_pool.credential_manager.get_current() if client_pool else None
            cred_id = current_cred.identifier if current_cred else "unknown"

            logger.error(f"Download attempt {attempt + 1} failed with credential '{cred_id}': {e}")

            # Try next credential if available
            if not _handle_operation_failure(
                client_pool, attempt, max_retries, cred_id, "Download"
            ):
                break

    # All retries exhausted
    if last_error:
        print(f"❌ Error downloading book: {last_error}")
        logger.error(f"Download failed after {max_retries} attempts: {last_error}")

    return None


def prompt_for_download(
    z_client: Zlibrary,
    books: List[Dict[str, Any]],
    client_pool: Optional[ZlibraryClientPool] = None,
    download_service: Any = None,
) -> None:
    """Prompt user to select and download a book from the list"""
    download_choice = input("\nEnter book number to download (or 'n' to skip): ").strip()
    if download_choice.lower() != "n":
        try:
            book_idx = int(download_choice) - 1
            if 0 <= book_idx < len(books):
                download_book(z_client, books[book_idx], client_pool, download_service=download_service)
            else:
                print("Invalid book number")
        except ValueError:
            print("Invalid input")


def handle_search_mode(
    z_client: Zlibrary, client_pool: Optional[ZlibraryClientPool] = None
) -> None:
    """Handle the search books option"""
    query = input("Enter search query: ").strip()
    if not query:
        print("Search query cannot be empty")
        return

    results = search_books(z_client, query, client_pool)
    if results and "books" in results and results["books"]:
        display_results(results)
        prompt_for_download(z_client, results["books"], client_pool)


def handle_popular_mode(
    z_client: Zlibrary, client_pool: Optional[ZlibraryClientPool] = None
) -> None:
    """Handle the popular books option"""
    try:
        print("\nFetching most popular books...")
        popular = z_client.getMostPopular()
        if popular and "books" in popular:
            display_results(popular)
            prompt_for_download(z_client, popular["books"], client_pool)
    except Exception as e:
        print(f"Error: {e}")


def handle_profile_mode(z_client: Zlibrary) -> None:
    """Handle the profile information option"""
    try:
        profile = z_client.getProfile()
        print("\nProfile Information:")
        print(f"Email: {profile.get('email', 'N/A')}")
        print(f"Name: {profile.get('name', 'N/A')}")
        print(f"Kindle Email: {profile.get('kindle_email', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")


def interactive_mode(z_client: Zlibrary, client_pool: Optional[ZlibraryClientPool] = None) -> None:
    """Interactive mode for searching and downloading books"""
    while True:
        print("\n" + "=" * 60)
        print("Z-Library Book Downloader")
        print("=" * 60)
        print("1. Search for books")
        print("2. Get most popular books")
        print("3. Get profile information")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            handle_search_mode(z_client, client_pool)
        elif choice == "2":
            handle_popular_mode(z_client, client_pool)
        elif choice == "3":
            handle_profile_mode(z_client)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def build_search_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Build search kwargs from command line arguments"""
    search_kwargs: Dict[str, Any] = {}
    arg_mapping = {
        "format": "format",
        "year_from": "year_from",
        "year_to": "year_to",
        "language": "language",
        "order": "order",
        "limit": "limit",
        "page": "page",
    }

    for arg_name, kwarg_name in arg_mapping.items():
        value = getattr(args, arg_name, None)
        if value:
            search_kwargs[kwarg_name] = value

    return search_kwargs


def handle_search_results(
    z_client: Zlibrary,
    results: Optional[Dict[str, Any]],
    download: bool,
    client_pool: Optional[ZlibraryClientPool] = None,
) -> None:
    """Handle search results and optional download"""
    if results and "books" in results and results["books"]:
        display_results(results)
        if download:
            print("\nDownloading first result...")
            download_book(z_client, results["books"][0], client_pool)
    else:
        print("No results found.")
        sys.exit(1)


def command_line_mode(
    z_client: Zlibrary, args: argparse.Namespace, client_pool: Optional[ZlibraryClientPool] = None
) -> None:
    """Command line mode for direct search and optional download"""
    search_kwargs = build_search_kwargs(args)
    save_to_db = getattr(args, "save_db", False)
    search_service = None

    # Initialize database services if --save-db flag is present
    if save_to_db:
        try:
            from .db_manager import DatabaseManager
            from .book_repository import BookRepository
            from .author_repository import AuthorRepository
            from .search_history_repository import SearchHistoryRepository
            from .search_service import SearchService

            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)
            search_repo = SearchHistoryRepository(db_manager)
            search_service = SearchService(book_repo, author_repo, search_repo)
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
            print(f"⚠️  Warning: Database initialization failed: {e}")
            print("Continuing search without database storage...")
            save_to_db = False

    results = search_books(z_client, args.title, client_pool, save_to_db, search_service,
                          **search_kwargs)
    handle_search_results(z_client, results, args.download, client_pool)


def tui_mode(z_client: Zlibrary) -> None:
    """Interactive TUI mode with rich library"""
    if not TUI_AVAILABLE:
        print("Error: TUI mode requires the 'rich' library")
        print("Install it with: pip install rich")
        sys.exit(1)

    tui = ZLibraryTUI(z_client)
    tui.run()


def add_mode_arguments(parser: argparse.ArgumentParser) -> None:
    """Add mode selection arguments to parser"""
    parser.add_argument(
        "--tui", action="store_true", help="Launch interactive TUI mode (recommended)"
    )
    parser.add_argument(
        "--classic", action="store_true", help="Use classic interactive mode instead of TUI"
    )


def add_search_arguments(parser: argparse.ArgumentParser) -> None:
    """Add search and filter arguments to parser"""
    parser.add_argument("--title", type=str, help="Book title to search for")
    parser.add_argument("--download", action="store_true", help="Download the first result")
    parser.add_argument("--save-db", action="store_true", help="Save search results to database")
    parser.add_argument(
        "--format", type=str, help="File format (pdf, epub, mobi, azw3, fb2, txt, djvu, etc.)"
    )
    parser.add_argument("--year-from", type=int, help="Filter books published from this year")
    parser.add_argument("--year-to", type=int, help="Filter books published until this year")
    parser.add_argument(
        "--language", type=str, help="Filter by language (english, spanish, french, etc.)"
    )
    parser.add_argument(
        "--order", type=str, choices=["popular", "year", "title"], help="Sort order for results"
    )
    parser.add_argument("--limit", type=int, help="Maximum number of results to return")
    parser.add_argument("--page", type=int, help="Page number for pagination")


def get_help_epilog() -> str:
    """Get the epilog text for argument parser help."""
    return """
Examples:
  TUI mode (interactive with rich UI):
    ./run.sh --tui

  Search only:
    ./run.sh --title "The Great Gatsby"

  Search and download:
    ./run.sh --title "Python Programming" --download

  Search with database storage:
    ./run.sh --title "Machine Learning" --save-db

  Search with filters:
    ./run.sh --title "Machine Learning" --format pdf --year-from 2020 --limit 10

  Advanced search:
    ./run.sh --title "Data Science" --format epub --language english --order year --download

  Search and save to database:
    ./run.sh --title "Python Programming" --save-db --format pdf --language english

  Database commands:
    ./run.sh db init                           # Initialize database
    ./run.sh db browse --language english      # Browse books
    ./run.sh db show 123                       # Show book details
    ./run.sh db save 123 --notes "Must read"   # Save book
    ./run.sh db saved                          # List saved books

Available formats: pdf, epub, mobi, azw3, fb2, txt, djvu, etc.
Available languages: english, spanish, french, german, russian, etc.
Available order: popular, year, title

Credential Configuration:
  This tool supports two credential formats:
  1. zlibrary_credentials.toml (recommended) - Multiple accounts with automatic rotation
  2. .env - Single account for backward compatibility

  For TOML format, create zlibrary_credentials.toml in the current directory.
  See zlibrary_credentials.toml.example for configuration template.
    """


def _add_db_browse_parser(db_subparsers: argparse._SubParsersAction) -> None:
    """Add db browse subcommand parser"""
    browse_parser = db_subparsers.add_parser("browse", help="Browse books in database")
    browse_parser.add_argument("--query", type=str, help="Search query for books")
    browse_parser.add_argument("--language", type=str, help="Filter by language")
    browse_parser.add_argument("--year-from", type=int, help="Filter from year")
    browse_parser.add_argument("--year-to", type=int, help="Filter to year")
    browse_parser.add_argument("--format", type=str, help="Filter by file format")
    browse_parser.add_argument("--author", type=str, help="Filter by author name")
    browse_parser.add_argument("--limit", type=int, default=50, help="Limit results")
    browse_parser.set_defaults(func="db_browse")


def _add_db_save_parser(db_subparsers: argparse._SubParsersAction) -> None:
    """Add db save subcommand parser"""
    save_parser = db_subparsers.add_parser("save", help="Save a book to collection")
    save_parser.add_argument("book_id", type=int, help="Book ID to save")
    save_parser.add_argument("--notes", type=str, help="Notes about the book")
    save_parser.add_argument("--tags", type=str, help="Comma-separated tags")
    save_parser.add_argument("--priority", type=int, choices=[1, 2, 3, 4, 5],
                           help="Priority (1-5)")
    save_parser.set_defaults(func="db_save")


def _add_simple_db_parsers(db_subparsers: argparse._SubParsersAction) -> None:
    """Add simple db subcommand parsers (init, show, unsave, saved)"""
    init_parser = db_subparsers.add_parser("init", help="Initialize the book database")
    init_parser.set_defaults(func="db_init")

    show_parser = db_subparsers.add_parser("show", help="Show detailed book information")
    show_parser.add_argument("book_id", type=int, help="Book ID to display")
    show_parser.set_defaults(func="db_show")

    unsave_parser = db_subparsers.add_parser("unsave", help="Remove book from collection")
    unsave_parser.add_argument("book_id", type=int, help="Book ID to unsave")
    unsave_parser.set_defaults(func="db_unsave")

    saved_parser = db_subparsers.add_parser("saved", help="List saved books")
    saved_parser.set_defaults(func="db_saved")


def _add_list_parsers(db_subparsers: argparse._SubParsersAction) -> None:
    """Add reading list subcommand parsers"""
    # list-create
    create_parser = db_subparsers.add_parser(
        "list-create", help="Create a new reading list"
    )
    create_parser.add_argument("name", type=str, help="Name for the reading list")
    create_parser.add_argument(
        "--description", type=str, help="Optional description"
    )
    create_parser.set_defaults(func="db_list_create")

    # list-show
    show_parser = db_subparsers.add_parser(
        "list-show", help="Show books in a reading list"
    )
    show_parser.add_argument("name", type=str, help="Name of the reading list")
    show_parser.set_defaults(func="db_list_show")

    # list-add
    add_parser = db_subparsers.add_parser(
        "list-add", help="Add a book to a reading list"
    )
    add_parser.add_argument("name", type=str, help="Name of the reading list")
    add_parser.add_argument("book_id", type=int, help="Book ID to add")
    add_parser.set_defaults(func="db_list_add")

    # list-remove
    remove_parser = db_subparsers.add_parser(
        "list-remove", help="Remove a book from a reading list"
    )
    remove_parser.add_argument("name", type=str, help="Name of the reading list")
    remove_parser.add_argument("book_id", type=int, help="Book ID to remove")
    remove_parser.set_defaults(func="db_list_remove")

    # list-delete
    delete_parser = db_subparsers.add_parser(
        "list-delete", help="Delete a reading list"
    )
    delete_parser.add_argument("name", type=str, help="Name of the reading list")
    delete_parser.set_defaults(func="db_list_delete")

    # lists
    lists_parser = db_subparsers.add_parser("lists", help="List all reading lists")
    lists_parser.set_defaults(func="db_lists")


def _add_utility_parsers(db_subparsers: argparse._SubParsersAction) -> None:
    """Add database utility subcommand parsers"""
    # downloads
    downloads_parser = db_subparsers.add_parser(
        "downloads", help="Show download history"
    )
    downloads_parser.add_argument("--recent", type=int, help="Days to look back")
    downloads_parser.add_argument("--credential", type=str, help="Filter by credential ID")
    downloads_parser.add_argument("--limit", type=int, default=50, help="Limit results")
    downloads_parser.set_defaults(func="db_downloads")

    # stats
    stats_parser = db_subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.set_defaults(func="db_stats")

    # export
    export_parser = db_subparsers.add_parser("export", help="Export books to file")
    export_parser.add_argument(
        "--format", type=str, choices=["json", "csv"], default="json",
        help="Export format"
    )
    export_parser.add_argument("--output", type=str, help="Output filename")
    export_parser.set_defaults(func="db_export")

    # import
    import_parser = db_subparsers.add_parser("import", help="Import books from JSON")
    import_parser.add_argument("input", type=str, help="Input JSON file")
    import_parser.set_defaults(func="db_import")

    # vacuum
    vacuum_parser = db_subparsers.add_parser("vacuum", help="Optimize database")
    vacuum_parser.set_defaults(func="db_vacuum")


def add_db_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Add database subcommand arguments to parser"""
    db_parser = subparsers.add_parser(
        "db",
        help="Database operations for managing book library",
        description="Manage local book database"
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database commands")
    _add_simple_db_parsers(db_subparsers)
    _add_db_browse_parser(db_subparsers)
    _add_db_save_parser(db_subparsers)
    _add_list_parsers(db_subparsers)
    _add_utility_parsers(db_subparsers)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description=(
            "Z-Library Book Downloader - " "Supports multiple credentials with automatic rotation"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=get_help_epilog(),
    )

    add_mode_arguments(parser)
    add_search_arguments(parser)

    # Add subparsers for db commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    add_db_arguments(subparsers)

    return parser


def select_and_run_mode(
    z_client: Zlibrary, args: argparse.Namespace, client_pool: Optional[ZlibraryClientPool] = None
) -> None:
    """Determine which mode to use and run it"""
    if args.title:
        # CLI mode with direct search
        command_line_mode(z_client, args, client_pool)
    elif args.tui:
        # TUI mode (rich interactive)
        tui_mode(z_client)
    elif args.classic:
        # Classic interactive mode
        interactive_mode(z_client, client_pool)
    else:
        # Default: Use TUI if available, otherwise classic
        if TUI_AVAILABLE:
            tui_mode(z_client)
        else:
            interactive_mode(z_client, client_pool)


def _get_db_command_handlers() -> Dict[str, Any]:
    """Get mapping of db command names to handler functions"""
    try:
        from . import db_commands
        return {
            'init': db_commands.db_init_command,
            'browse': db_commands.db_browse_command,
            'show': db_commands.db_show_command,
            'save': db_commands.db_save_command,
            'unsave': db_commands.db_unsave_command,
            'saved': db_commands.db_saved_command,
            'list-create': db_commands.db_list_create_command,
            'list-show': db_commands.db_list_show_command,
            'list-add': db_commands.db_list_add_command,
            'list-remove': db_commands.db_list_remove_command,
            'list-delete': db_commands.db_list_delete_command,
            'lists': db_commands.db_lists_command,
            'downloads': db_commands.db_downloads_command,
            'stats': db_commands.db_stats_command,
            'export': db_commands.db_export_command,
            'import': db_commands.db_import_command,
            'vacuum': db_commands.db_vacuum_command,
        }
    except ImportError:
        print("Error: Database commands module not available yet")
        print("Database functionality will be available in the next release")
        sys.exit(1)


def handle_db_commands(args: argparse.Namespace) -> None:
    """Route db commands to appropriate handlers"""
    if not hasattr(args, 'db_command') or args.db_command is None:
        print("Error: No database command specified")
        print("Use 'db --help' to see available commands")
        sys.exit(1)

    command_map = _get_db_command_handlers()
    handler = command_map.get(args.db_command)
    if handler:
        handler(args)
    else:
        print(f"Error: Unknown db command: {args.db_command}")
        sys.exit(1)


def main() -> None:
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Check if this is a db command
    if hasattr(args, 'command') and args.command == 'db':
        handle_db_commands(args)
        return

    print("Z-Library Book Downloader")
    print("=" * 60)

    # Load credentials and initialize client pool
    credential_manager, client_pool = load_credentials()

    # Display credential status
    display_credential_status(credential_manager)

    # Initialize client
    z_client = initialize_zlibrary(client_pool)
    print("\nLogin successful!")

    # Run the appropriate mode
    select_and_run_mode(z_client, args, client_pool)


if __name__ == "__main__":
    main()
