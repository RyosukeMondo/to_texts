#!/usr/bin/env python3
"""
Test script for download and extract functionality of to_texts project
Tests search, download, and extraction capabilities with diagnostics
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

def check_python_env() -> bool:
    """Check if Python environment is properly set up"""
    print("=" * 60)
    print("1. Checking Python Environment")
    print("=" * 60)

    try:
        # Check required packages
        import requests
        import rich
        from zlibrary_downloader.client import Zlibrary
        from zlibrary_downloader.cli import load_credentials
        print("✓ All Python packages found")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("  Run: pip install -r packages/python/zlibrary-downloader/requirements.txt")
        return False

def check_rust_binary() -> bool:
    """Check if Rust text-extractor binary is built"""
    print("\n" + "=" * 60)
    print("2. Checking Rust Text Extractor")
    print("=" * 60)

    binary_path = Path("packages/rust/target/release/text-extractor")
    if binary_path.exists() and os.access(binary_path, os.X_OK):
        print(f"✓ Rust binary found at: {binary_path}")
        return True
    else:
        print(f"✗ Rust binary not found at: {binary_path}")
        print("  Run: cd packages/rust && cargo build --release")
        return False

def check_credentials() -> Optional[Dict[str, str]]:
    """Check if Z-Library credentials are configured"""
    print("\n" + "=" * 60)
    print("3. Checking Z-Library Credentials")
    print("=" * 60)

    env_path = Path("packages/python/zlibrary-downloader/.env")

    if not env_path.exists():
        print(f"✗ .env file not found at: {env_path}")
        print("\n  To configure credentials:")
        print("  1. Copy .env.example to .env:")
        print("     cp packages/python/zlibrary-downloader/.env.example packages/python/zlibrary-downloader/.env")
        print("\n  2. Add your Z-Library credentials to the .env file")
        print("     Option A (Recommended): Remix credentials from browser cookies")
        print("       ZLIBRARY_REMIX_USERID=your_userid")
        print("       ZLIBRARY_REMIX_USERKEY=your_userkey")
        print("     Option B: Email and Password")
        print("       ZLIBRARY_EMAIL=your_email@example.com")
        print("       ZLIBRARY_PASSWORD=your_password")
        return None

    load_dotenv(env_path)
    remix_userid = os.getenv("ZLIBRARY_REMIX_USERID")
    remix_userkey = os.getenv("ZLIBRARY_REMIX_USERKEY")
    email = os.getenv("ZLIBRARY_EMAIL")
    password = os.getenv("ZLIBRARY_PASSWORD")

    if remix_userid and remix_userkey:
        print("✓ Remix credentials found")
        return {"type": "remix", "userid": remix_userid, "userkey": remix_userkey}
    elif email and password:
        print("✓ Email/Password credentials found")
        return {"type": "email", "email": email, "password": password}
    else:
        print("✗ No valid credentials found in .env file")
        return None

def test_extraction() -> bool:
    """Test the extraction functionality with existing downloaded files"""
    print("\n" + "=" * 60)
    print("4. Testing Text Extraction")
    print("=" * 60)

    download_dir = Path("packages/python/zlibrary-downloader/downloads")

    if not download_dir.exists() or not list(download_dir.glob("*.epub")) and not list(download_dir.glob("*.pdf")):
        print(f"✗ No downloaded books found in: {download_dir}")
        print("  Download some books first to test extraction")
        return False

    print(f"Found books to extract in: {download_dir}")

    # Create output directory
    output_dir = Path("/tmp/to_texts_test_extract")
    output_dir.mkdir(exist_ok=True)

    try:
        result = subprocess.run(
            [
                "./packages/rust/target/release/text-extractor",
                "--target", str(download_dir),
                "--output", str(output_dir)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✓ Text extraction successful")
            print(f"  Output saved to: {output_dir}")
            # Count extracted files
            extracted_count = len(list(output_dir.glob("*.txt")))
            print(f"  Extracted {extracted_count} files")
            return True
        else:
            print(f"✗ Extraction failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        return False

def test_search_capability() -> bool:
    """Test search capability with credentials"""
    print("\n" + "=" * 60)
    print("4. Testing Search Capability")
    print("=" * 60)

    creds = check_credentials()
    if not creds:
        print("⊘ Skipping search test: credentials not configured")
        return False

    try:
        from zlibrary_downloader.client import Zlibrary

        if creds["type"] == "remix":
            print("Initializing with remix credentials...")
            client = Zlibrary(
                remix_userid=creds["userid"],
                remix_userkey=creds["userkey"]
            )
        else:
            print("Initializing with email/password...")
            client = Zlibrary(
                email=creds["email"],
                password=creds["password"]
            )

        if not client.isLoggedIn():
            print("✗ Failed to authenticate with Z-Library")
            return False

        print("✓ Successfully authenticated with Z-Library")

        # Test search for 2025 books
        print("Searching for books published in 2025...")
        results = client.search(message="python", yearFrom=2025, yearTo=2025, limit=5)

        if results and "books" in results:
            books = results["books"]
            print(f"✓ Found {len(books)} books from 2025")
            for i, book in enumerate(books[:3], 1):
                print(f"  {i}. {book.get('title', 'Unknown')} ({book.get('year', 'N/A')})")
            return True
        else:
            print("✗ No books found or search failed")
            return False

    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def run_full_test_suite() -> None:
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " to_texts - Download & Extract Functionality Test ".center(58) + "║")
    print("╚" + "=" * 58 + "╝\n")

    results = {
        "Python Environment": check_python_env(),
        "Rust Binary": check_rust_binary(),
        "Text Extraction": test_extraction(),
        "Search & Download": test_search_capability(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    passed = sum(results.values())
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        if not results["Python Environment"]:
            print("• Install Python dependencies:")
            print("  pip install -r packages/python/zlibrary-downloader/requirements.txt")
        if not results["Rust Binary"]:
            print("• Build Rust text extractor:")
            print("  cd packages/rust && cargo build --release")
        if not results["Text Extraction"]:
            print("• Download some books first:")
            print("  ./packages/python/zlibrary-downloader/run.sh --title 'Python'")
        if not results["Search & Download"]:
            print("• Configure Z-Library credentials in:")
            print("  packages/python/zlibrary-downloader/.env")

if __name__ == "__main__":
    run_full_test_suite()
