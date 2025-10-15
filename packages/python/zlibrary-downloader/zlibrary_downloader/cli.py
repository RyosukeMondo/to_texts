#!/usr/bin/env python3
"""
Z-Library Book Downloader
Search and download books from Z-Library using credentials from .env file
"""

import os
import sys
import argparse
from typing import Dict, Optional, Any, List
from .client import Zlibrary
from dotenv import load_dotenv

# Try to import TUI module (optional)
try:
    from .tui import ZLibraryTUI

    TUI_AVAILABLE = True
except ImportError:
    TUI_AVAILABLE = False


def load_credentials() -> Dict[str, Optional[str]]:
    """Load credentials from .env file"""
    load_dotenv()

    # Try to get remix credentials first (recommended)
    remix_userid = os.getenv("ZLIBRARY_REMIX_USERID")
    remix_userkey = os.getenv("ZLIBRARY_REMIX_USERKEY")

    # Fall back to email/password if remix not available
    email = os.getenv("ZLIBRARY_EMAIL")
    password = os.getenv("ZLIBRARY_PASSWORD")

    return {
        "email": email,
        "password": password,
        "remix_userid": remix_userid,
        "remix_userkey": remix_userkey,
    }


def initialize_zlibrary(credentials: Dict[str, Optional[str]]) -> Zlibrary:
    """Initialize Z-Library client with credentials"""
    if credentials["remix_userid"] and credentials["remix_userkey"]:
        print("Logging in with remix credentials...")
        return Zlibrary(
            remix_userid=credentials["remix_userid"], remix_userkey=credentials["remix_userkey"]
        )
    elif credentials["email"] and credentials["password"]:
        print("Logging in with email/password...")
        return Zlibrary(email=credentials["email"], password=credentials["password"])
    else:
        print("Error: No valid credentials found in .env file")
        print(
            "Please set either ZLIBRARY_EMAIL/ZLIBRARY_PASSWORD or "
            "ZLIBRARY_REMIX_USERID/ZLIBRARY_REMIX_USERKEY"
        )
        sys.exit(1)


def search_books(z_client: Zlibrary, query: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
    """Search for books on Z-Library with optional filters"""
    print(f"\nSearching for: {query}")

    # Build search parameters
    search_params: Dict[str, Any] = {"message": query}

    # Add optional parameters if provided
    if kwargs.get("format"):
        search_params["extensions"] = kwargs["format"]
    if kwargs.get("year_from"):
        search_params["yearFrom"] = kwargs["year_from"]
    if kwargs.get("year_to"):
        search_params["yearTo"] = kwargs["year_to"]
    if kwargs.get("language"):
        search_params["languages"] = kwargs["language"]
    if kwargs.get("order"):
        search_params["order"] = kwargs["order"]
    if kwargs.get("limit"):
        search_params["limit"] = kwargs["limit"]
    if kwargs.get("page"):
        search_params["page"] = kwargs["page"]

    try:
        results = z_client.search(**search_params)
        return results
    except Exception as e:
        print(f"Error searching: {e}")
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


def download_book(
    z_client: Zlibrary, book: Dict[str, Any], download_dir: str = "downloads"
) -> Optional[str]:
    """Download a book"""
    # Create downloads directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    try:
        print(f"Downloading: {book.get('title', 'Unknown')}")
        filename, filecontent = z_client.downloadBook(book)

        # Save the file
        filepath = os.path.join(download_dir, filename)
        with open(filepath, "wb") as bookfile:
            bookfile.write(filecontent)

        print(f"Successfully downloaded to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading book: {e}")
        return None


def prompt_for_download(z_client: Zlibrary, books: List[Dict[str, Any]]) -> None:
    """Prompt user to select and download a book from the list"""
    download_choice = input("\nEnter book number to download (or 'n' to skip): ").strip()
    if download_choice.lower() != "n":
        try:
            book_idx = int(download_choice) - 1
            if 0 <= book_idx < len(books):
                download_book(z_client, books[book_idx])
            else:
                print("Invalid book number")
        except ValueError:
            print("Invalid input")


def handle_search_mode(z_client: Zlibrary) -> None:
    """Handle the search books option"""
    query = input("Enter search query: ").strip()
    if not query:
        print("Search query cannot be empty")
        return

    results = search_books(z_client, query)
    if results and "books" in results and results["books"]:
        display_results(results)
        prompt_for_download(z_client, results["books"])


def handle_popular_mode(z_client: Zlibrary) -> None:
    """Handle the popular books option"""
    try:
        print("\nFetching most popular books...")
        popular = z_client.getMostPopular()
        if popular and "books" in popular:
            display_results(popular)
            prompt_for_download(z_client, popular["books"])
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


def interactive_mode(z_client: Zlibrary) -> None:
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
            handle_search_mode(z_client)
        elif choice == "2":
            handle_popular_mode(z_client)
        elif choice == "3":
            handle_profile_mode(z_client)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def command_line_mode(z_client: Zlibrary, args: argparse.Namespace) -> None:
    """Command line mode for direct search and optional download"""
    # Prepare search filters
    search_kwargs: Dict[str, Any] = {}
    if args.format:
        search_kwargs["format"] = args.format
    if args.year_from:
        search_kwargs["year_from"] = args.year_from
    if args.year_to:
        search_kwargs["year_to"] = args.year_to
    if args.language:
        search_kwargs["language"] = args.language
    if args.order:
        search_kwargs["order"] = args.order
    if args.limit:
        search_kwargs["limit"] = args.limit
    if args.page:
        search_kwargs["page"] = args.page

    results = search_books(z_client, args.title, **search_kwargs)

    if results and "books" in results and results["books"]:
        display_results(results)

        # Download the first result if --download flag is set
        if args.download:
            print("\nDownloading first result...")
            download_book(z_client, results["books"][0])
    else:
        print("No results found.")
        sys.exit(1)


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


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Z-Library Book Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
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
        """,
    )

    add_mode_arguments(parser)
    add_search_arguments(parser)
    return parser


def select_and_run_mode(z_client: Zlibrary, args: argparse.Namespace) -> None:
    """Determine which mode to use and run it"""
    if args.title:
        # CLI mode with direct search
        command_line_mode(z_client, args)
    elif args.tui:
        # TUI mode (rich interactive)
        tui_mode(z_client)
    elif args.classic:
        # Classic interactive mode
        interactive_mode(z_client)
    else:
        # Default: Use TUI if available, otherwise classic
        if TUI_AVAILABLE:
            tui_mode(z_client)
        else:
            interactive_mode(z_client)


def main() -> None:
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()

    print("Z-Library Book Downloader")
    print("=" * 60)

    # Load credentials and initialize client
    credentials = load_credentials()
    z_client = initialize_zlibrary(credentials)
    print("Login successful!")

    # Run the appropriate mode
    select_and_run_mode(z_client, args)


if __name__ == "__main__":
    main()
