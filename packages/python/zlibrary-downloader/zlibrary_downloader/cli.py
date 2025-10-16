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
    z_client: Zlibrary, query: str, client_pool: Optional[ZlibraryClientPool] = None, **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """
    Search for books on Z-Library with optional filters.

    Automatically rotates to next credential after successful search when
    using multi-credential setup. Implements retry logic with next credential
    on failures.

    Args:
        z_client: Z-Library client to use for search
        query: Search query string
        client_pool: Optional client pool for credential rotation
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
) -> Optional[str]:
    """
    Download a book from Z-Library.

    Automatically rotates to next credential and updates download limits
    after successful download when using multi-credential setup. Implements
    retry logic with next credential on failures.

    Args:
        z_client: Z-Library client to use for download
        book: Book metadata dictionary
        client_pool: Optional client pool for credential rotation
        download_dir: Directory to save downloaded books

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
) -> None:
    """Prompt user to select and download a book from the list"""
    download_choice = input("\nEnter book number to download (or 'n' to skip): ").strip()
    if download_choice.lower() != "n":
        try:
            book_idx = int(download_choice) - 1
            if 0 <= book_idx < len(books):
                download_book(z_client, books[book_idx], client_pool)
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
    results = search_books(z_client, args.title, client_pool, **search_kwargs)
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

  Search with filters:
    ./run.sh --title "Machine Learning" --format pdf --year-from 2020 --limit 10

  Advanced search:
    ./run.sh --title "Data Science" --format epub --language english --order year --download

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


def main() -> None:
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()

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
