#!/usr/bin/env python3
"""
Test script to explore zlibrary API responses and available metadata.

This script will:
1. Connect to zlibrary using your credentials
2. Perform sample searches
3. Get detailed book info
4. Document all available metadata fields

Usage:
    python test_zlibrary_metadata.py

Prerequisites:
    - zlibrary-downloader package installed
    - Credentials configured in zlibrary_credentials.toml or .env
"""

import json
import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent / "packages/python/zlibrary-downloader"))

from zlibrary_downloader.client import Zlibrary
from zlibrary_downloader.credential_manager import CredentialManager


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def pretty_print_json(data: dict, title: str = "") -> None:
    """Pretty print JSON data."""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_search_metadata(client: Zlibrary) -> dict:
    """Test search endpoint and capture metadata structure."""
    print_section("Testing Search API")

    # Test basic search
    print("Performing search for 'python programming'...")
    results = client.search(message="python programming", limit=3)

    if results and "books" in results and len(results["books"]) > 0:
        print(f"\nFound {len(results['books'])} books")
        print("\nSample book structure:")
        sample_book = results["books"][0]
        pretty_print_json(sample_book)

        print("\n\nAll fields found in search results:")
        all_fields = set()
        for book in results["books"]:
            all_fields.update(book.keys())
        print(f"  Fields: {sorted(all_fields)}")

        return sample_book
    else:
        print("No results found or error occurred")
        pretty_print_json(results)
        return {}


def test_book_info_metadata(client: Zlibrary, book: dict) -> None:
    """Test getBookInfo endpoint for detailed metadata."""
    print_section("Testing Book Info API (Detailed Metadata)")

    if not book or "id" not in book or "hash" not in book:
        print("No book data available to test")
        return

    print(f"Getting detailed info for book ID: {book['id']}")
    book_info = client.getBookInfo(book["id"], book["hash"])

    if book_info:
        pretty_print_json(book_info, "Detailed book info")

        if "book" in book_info:
            print("\n\nAll fields in detailed book info:")
            print(f"  Fields: {sorted(book_info['book'].keys())}")
    else:
        print("No book info found")


def test_similar_books(client: Zlibrary, book: dict) -> None:
    """Test getSimilar endpoint."""
    print_section("Testing Similar Books API")

    if not book or "id" not in book or "hash" not in book:
        print("No book data available to test")
        return

    print(f"Getting similar books for book ID: {book['id']}")
    similar = client.getSimilar(book["id"], book["hash"])

    if similar and "books" in similar and len(similar["books"]) > 0:
        print(f"Found {len(similar['books'])} similar books")
        print("\nSample similar book:")
        pretty_print_json(similar["books"][0])


def test_book_formats(client: Zlibrary, book: dict) -> None:
    """Test getBookForamt endpoint."""
    print_section("Testing Book Formats API")

    if not book or "id" not in book or "hash" not in book:
        print("No book data available to test")
        return

    print(f"Getting available formats for book ID: {book['id']}")
    formats = client.getBookForamt(book["id"], book["hash"])

    if formats:
        pretty_print_json(formats, "Available formats")


def test_user_profile(client: Zlibrary) -> None:
    """Test user profile endpoint."""
    print_section("Testing User Profile API")

    profile = client.getProfile()
    if profile and "user" in profile:
        pretty_print_json(profile, "User profile")
        print("\n\nUser profile fields:")
        print(f"  Fields: {sorted(profile['user'].keys())}")


def test_popular_books(client: Zlibrary) -> None:
    """Test most popular books endpoint."""
    print_section("Testing Most Popular Books API")

    popular = client.getMostPopular()
    if popular and "books" in popular and len(popular["books"]) > 0:
        print(f"Found {len(popular['books'])} popular books")
        print("\nSample popular book:")
        pretty_print_json(popular["books"][0])


def test_recently_added(client: Zlibrary) -> None:
    """Test recently added books endpoint."""
    print_section("Testing Recently Added Books API")

    recent = client.getRecently()
    if recent and "books" in recent and len(recent["books"]) > 0:
        print(f"Found {len(recent['books'])} recent books")
        print("\nSample recent book:")
        pretty_print_json(recent["books"][0])


def test_user_downloaded(client: Zlibrary) -> None:
    """Test user downloaded books endpoint."""
    print_section("Testing User Downloaded Books API")

    downloaded = client.getUserDownloaded(limit=5)
    if downloaded and "books" in downloaded:
        if len(downloaded["books"]) > 0:
            print(f"Found {len(downloaded['books'])} downloaded books")
            print("\nSample downloaded book:")
            pretty_print_json(downloaded["books"][0])
        else:
            print("No downloaded books yet")


def test_user_saved(client: Zlibrary) -> None:
    """Test user saved books endpoint."""
    print_section("Testing User Saved Books API")

    saved = client.getUserSaved(limit=5)
    if saved and "books" in saved:
        if len(saved["books"]) > 0:
            print(f"Found {len(saved['books'])} saved books")
            print("\nSample saved book:")
            pretty_print_json(saved["books"][0])
        else:
            print("No saved books yet")


def test_available_languages(client: Zlibrary) -> None:
    """Test available languages endpoint."""
    print_section("Testing Available Languages API")

    languages = client.getLanguages()
    if languages:
        pretty_print_json(languages, "Available languages")


def test_available_extensions(client: Zlibrary) -> None:
    """Test available extensions endpoint."""
    print_section("Testing Available Extensions API")

    extensions = client.getExtensions()
    if extensions:
        pretty_print_json(extensions, "Available extensions")


def main():
    """Main test function."""
    print_section("Z-Library Metadata Explorer")

    # Load credentials
    print("Loading credentials...")
    try:
        cred_manager = CredentialManager()
        cred_manager.load_credentials()

        if not cred_manager.credentials:
            print("\nError: No credentials found!")
            print("Please configure credentials in:")
            print("  - zlibrary_credentials.toml (recommended)")
            print("  - or .env file")
            sys.exit(1)

        cred = cred_manager.get_current()
        print(f"Using credential: {cred.identifier}")

    except Exception as e:
        print(f"\nError loading credentials: {e}")
        sys.exit(1)

    # Create client
    print("\nInitializing Z-Library client...")
    if cred.email and cred.password:
        client = Zlibrary(email=cred.email, password=cred.password)
    elif cred.remix_userid and cred.remix_userkey:
        client = Zlibrary(remix_userid=cred.remix_userid, remix_userkey=cred.remix_userkey)
    else:
        print("Error: Invalid credential format")
        sys.exit(1)

    if not client.isLoggedIn():
        print("Error: Failed to login to Z-Library")
        sys.exit(1)

    print("Successfully logged in!")

    # Run all tests
    sample_book = test_search_metadata(client)
    test_book_info_metadata(client, sample_book)
    test_similar_books(client, sample_book)
    test_book_formats(client, sample_book)
    test_user_profile(client)
    test_popular_books(client)
    test_recently_added(client)
    test_user_downloaded(client)
    test_user_saved(client)
    test_available_languages(client)
    test_available_extensions(client)

    print_section("Test Complete")
    print("\nAll metadata has been captured above.")
    print("Review the output to see all available fields from Z-Library API.")


if __name__ == "__main__":
    main()
