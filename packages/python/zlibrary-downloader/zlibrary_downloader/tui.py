#!/usr/bin/env python3
"""
Z-Library TUI (Text User Interface)
Interactive interface using rich library
"""

from typing import Any, Dict, List, Optional, Literal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box


console = Console()


class ZLibraryTUI:
    """TUI for Z-Library downloader"""

    FORMATS: List[str] = ["pdf", "epub", "mobi", "azw3", "fb2", "txt", "djvu", "doc", "docx", "rtf"]
    LANGUAGES: List[str] = [
        "english",
        "spanish",
        "french",
        "german",
        "russian",
        "italian",
        "portuguese",
        "chinese",
        "japanese",
        "korean",
        "arabic",
    ]
    SORT_ORDERS: List[str] = ["popular", "year", "title"]

    def __init__(self, z_client: Any, client_pool: Any = None) -> None:
        self.z_client: Any = z_client
        self.client_pool: Any = client_pool
        self.current_results: Optional[List[Dict[str, Any]]] = None

    def show_welcome(self) -> None:
        """Display welcome banner"""
        welcome_text = Text()
        welcome_text.append("Z-Library Book Downloader\n", style="bold cyan")
        welcome_text.append("Interactive TUI Mode", style="dim")

        panel = Panel(welcome_text, border_style="cyan", box=box.DOUBLE)
        console.print(panel)
        console.print()

    def _prompt_for_title(self, params: Dict[str, Any]) -> None:
        """Prompt for required title parameter"""
        while True:
            title = Prompt.ask("[yellow]Book title or search query[/yellow] [red]*required[/red]")
            if title.strip():
                params["title"] = title.strip()
                break
            console.print("[red]Title is required![/red]")

    def _prompt_for_format(self, params: Dict[str, Any]) -> None:
        """Prompt for optional file format filter"""
        if Confirm.ask("\n[cyan]Filter by file format?[/cyan]", default=False):
            console.print(f"Available formats: [dim]{', '.join(self.FORMATS)}[/dim]")
            format_choice = Prompt.ask(
                "[yellow]Format[/yellow]", choices=self.FORMATS + [""], default=""
            )
            if format_choice:
                params["format"] = format_choice

    def _prompt_for_year_range(self, params: Dict[str, Any]) -> None:
        """Prompt for optional publication year range"""
        if not Confirm.ask("\n[cyan]Filter by publication year?[/cyan]", default=False):
            return

        year_from = IntPrompt.ask("[yellow]From year[/yellow] (e.g., 2020)", default=None)
        if year_from:
            if year_from < 1800 or year_from > 2100:
                console.print("[yellow]Warning: Year adjusted to reasonable range[/yellow]")
                year_from = max(1800, min(2100, year_from))
            params["year_from"] = year_from

        year_to = IntPrompt.ask("[yellow]To year[/yellow] (e.g., 2024)", default=None)
        if year_to:
            if year_to < 1800 or year_to > 2100:
                console.print("[yellow]Warning: Year adjusted to reasonable range[/yellow]")
                year_to = max(1800, min(2100, year_to))

            if year_from and year_to < year_from:
                console.print("[red]'To year' must be >= 'From year'. Swapping values.[/red]")
                year_from, year_to = year_to, year_from
                params["year_from"] = year_from

            params["year_to"] = year_to

    def _prompt_for_language(self, params: Dict[str, Any]) -> None:
        """Prompt for optional language filter"""
        if Confirm.ask("\n[cyan]Filter by language?[/cyan]", default=False):
            console.print(f"Available languages: [dim]{', '.join(self.LANGUAGES)}[/dim]")
            lang_choice = Prompt.ask(
                "[yellow]Language[/yellow]", choices=self.LANGUAGES + [""], default=""
            )
            if lang_choice:
                params["language"] = lang_choice

    def _prompt_for_sort_order(self, params: Dict[str, Any]) -> None:
        """Prompt for optional sort order"""
        if Confirm.ask("\n[cyan]Sort results?[/cyan]", default=False):
            sort_choice = Prompt.ask(
                "[yellow]Sort by[/yellow]", choices=self.SORT_ORDERS, default="popular"
            )
            params["order"] = sort_choice

    def _prompt_for_limit(self, params: Dict[str, Any]) -> None:
        """Prompt for optional result limit"""
        if Confirm.ask("\n[cyan]Limit number of results?[/cyan]", default=False):
            limit = IntPrompt.ask("[yellow]Maximum results[/yellow] (1-100)", default=20)
            limit = max(1, min(100, limit))
            params["limit"] = limit

    def _prompt_for_page(self, params: Dict[str, Any]) -> None:
        """Prompt for optional page number"""
        if Confirm.ask("\n[cyan]Specify page number?[/cyan]", default=False):
            page = IntPrompt.ask("[yellow]Page number[/yellow] (min: 1)", default=1)
            page = max(1, page)
            params["page"] = page


    def _prompt_for_multi_page(self, params: Dict[str, Any]) -> None:
        """Prompt for multi-page search options"""
        multi_page = Confirm.ask(
            "[yellow]Enable multi-page search?[/yellow]", default=False, console=console
        )
        
        if multi_page:
            all_pages = Confirm.ask(
                "[yellow]Search ALL pages until no more results?[/yellow]", 
                default=False, 
                console=console
            )
            
            if all_pages:
                params["all_pages"] = True
                console.print("[green]Will search all available pages[/green]")
            else:
                max_pages_input = Prompt.ask(
                    "[yellow]Maximum number of pages to search[/yellow]",
                    default="5",
                    console=console,
                )
                try:
                    max_pages = int(max_pages_input)
                    if max_pages > 0:
                        params["max_pages"] = max_pages
                        console.print(f"[green]Will search up to {max_pages} pages[/green]")
                except ValueError:
                    console.print("[red]Invalid number, using single page search[/red]")

    def _prompt_for_save_db(self, params: Dict[str, Any]) -> None:
        """Prompt for saving results to database"""
        save_db = Confirm.ask(
            "[yellow]Save search results to database?[/yellow]", default=False, console=console
        )
        if save_db:
            params["save_db"] = True
            console.print("[green]Results will be saved to database[/green]")

    def get_search_params(self) -> Dict[str, Any]:
        """Interactively collect search parameters"""
        console.print("\n[bold cyan]Search Parameters[/bold cyan]", style="bold")
        console.print("Press Enter to skip optional fields\n")

        params: Dict[str, Any] = {}

        self._prompt_for_title(params)
        self._prompt_for_format(params)
        self._prompt_for_year_range(params)
        self._prompt_for_language(params)
        self._prompt_for_sort_order(params)
        self._prompt_for_limit(params)
        self._prompt_for_page(params)
        self._prompt_for_multi_page(params)
        self._prompt_for_save_db(params)

        return params

    def display_search_params(self, params: Dict[str, Any]) -> None:
        """Display search parameters in a nice panel"""
        param_text = Text()
        param_text.append("Title: ", style="bold")
        param_text.append(f"{params.get('title', 'N/A')}\n")

        if params.get("format"):
            param_text.append("Format: ", style="bold")
            param_text.append(f"{params['format']}\n")

        if params.get("year_from") or params.get("year_to"):
            param_text.append("Year Range: ", style="bold")
            year_range = f"{params.get('year_from', 'Any')} - {params.get('year_to', 'Any')}"
            param_text.append(f"{year_range}\n")

        if params.get("language"):
            param_text.append("Language: ", style="bold")
            param_text.append(f"{params['language']}\n")

        if params.get("order"):
            param_text.append("Sort: ", style="bold")
            param_text.append(f"{params['order']}\n")

        if params.get("limit"):
            param_text.append("Limit: ", style="bold")
            param_text.append(f"{params['limit']} results\n")

        if params.get("page"):
            param_text.append("Page: ", style="bold")
            param_text.append(f"{params['page']}\n")

        # New multi-page parameters
        if params.get("all_pages"):
            param_text.append("Multi-page: ", style="bold green")
            param_text.append("All pages (until exhausted)\n", style="green")
        elif params.get("max_pages"):
            param_text.append("Multi-page: ", style="bold green")
            param_text.append(f"Up to {params['max_pages']} pages\n", style="green")

        if params.get("save_db"):
            param_text.append("Database: ", style="bold yellow")
            param_text.append("Save results to database\n", style="yellow")

        panel = Panel(
            param_text, title="[bold cyan]Search Parameters[/bold cyan]", border_style="cyan"
        )
        console.print("\n", panel)

    def search_with_progress(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search with a progress indicator"""
        # Check if multi-page search or save-to-db is enabled
        max_pages = params.get("max_pages")
        all_pages = params.get("all_pages", False)
        save_db = params.get("save_db", False)
        
        # If multi-page or save-db, we need to use CLI functions
        if max_pages or all_pages or save_db:
            # Import necessary modules for multi-page and save-db
            from . import cli
            
            # Initialize search service if save_db is enabled
            search_service = None
            if save_db:
                try:
                    from .db_manager import DatabaseManager
                    from .book_repository import BookRepository
                    from .author_repository import AuthorRepository
                    from .search_history_repository import SearchHistoryRepository
                    from .search_service import SearchService

                    console.print("[yellow]Initializing database...[/yellow]")
                    db_manager = DatabaseManager()
                    db_manager.initialize_schema()

                    book_repo = BookRepository(db_manager)
                    author_repo = AuthorRepository(db_manager)
                    search_repo = SearchHistoryRepository(db_manager)
                    search_service = SearchService(book_repo, author_repo, search_repo)
                    console.print("[green]✓ Database ready[/green]")
                except Exception as e:
                    console.print(f"[red]⚠️  Warning: Database initialization failed: {e}[/red]")
                    console.print("[yellow]Continuing search without database storage...[/yellow]")
                    save_db = False
            
            # Build search kwargs using ORIGINAL parameter names (not API names)
            # The CLI functions will convert them to API names internally
            search_kwargs = {}
            if params.get("format"):
                search_kwargs["format"] = params["format"]
            if params.get("year_from"):
                search_kwargs["year_from"] = params["year_from"]
            if params.get("year_to"):
                search_kwargs["year_to"] = params["year_to"]
            if params.get("language"):
                search_kwargs["language"] = params["language"]
            if params.get("order"):
                search_kwargs["order"] = params["order"]
            if params.get("limit"):
                search_kwargs["limit"] = params["limit"]
            if params.get("page"):
                search_kwargs["page"] = params["page"]
            
            # Use multi-page search if enabled
            if max_pages or all_pages:
                return cli.search_books_multi_page(
                    self.z_client,
                    params["title"],
                    self.client_pool,
                    save_db,
                    search_service,
                    max_pages=max_pages,
                    all_pages=all_pages,
                    **search_kwargs,
                )
            else:
                # Single page with save_db
                return cli.search_books(
                    self.z_client,
                    params["title"],
                    self.client_pool,
                    save_db,
                    search_service,
                    **search_kwargs,
                )
        
        # Original single-page search without save-db
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Searching Z-Library...", total=None)

            # Build search kwargs with proper API parameter names
            search_kwargs = {"message": params["title"]}

            # Map our parameter names to Z-Library API names
            if params.get("format"):
                search_kwargs["extensions"] = params["format"]
            if params.get("year_from"):
                search_kwargs["yearFrom"] = params["year_from"]
            if params.get("year_to"):
                search_kwargs["yearTo"] = params["year_to"]
            if params.get("language"):
                search_kwargs["languages"] = params["language"]
            if params.get("order"):
                search_kwargs["order"] = params["order"]
            if params.get("limit"):
                search_kwargs["limit"] = params["limit"]
            if params.get("page"):
                search_kwargs["page"] = params["page"]

            try:
                # Perform search
                results: Dict[str, Any] = self.z_client.search(**search_kwargs)
                progress.update(task, completed=True)
                return results
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Error during search: {e}[/red]")
                return None

    def display_results_table(self, results: Optional[Dict[str, Any]]) -> bool:
        """Display search results in a rich table"""
        if not results or "books" not in results or not results["books"]:
            console.print("\n[yellow]No results found[/yellow]")
            return False

        books = results["books"]
        self.current_results = books

        # Create table
        table = Table(
            title=f"[bold cyan]Found {len(books)} Books[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Title", style="cyan", no_wrap=False, max_width=50)
        table.add_column("Author", style="green", max_width=25)
        table.add_column("Year", justify="center", width=6)
        table.add_column("Format", justify="center", width=7)
        table.add_column("Language", width=10)

        for idx, book in enumerate(books, 1):
            table.add_row(
                str(idx),
                book.get("title", "N/A"),
                book.get("author", "N/A"),
                str(book.get("year", "N/A")),
                book.get("extension", "N/A").upper(),
                book.get("language", "N/A"),
            )

        console.print("\n", table)
        return True

    def download_with_progress(
        self, book: Dict[str, Any], download_dir: str = "downloads"
    ) -> Optional[str]:
        """Download a book with progress indicator"""
        import os

        os.makedirs(download_dir, exist_ok=True)

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task(
                f"Downloading: {book.get('title', 'Unknown')[:50]}...", total=None
            )

            try:
                filename, filecontent = self.z_client.downloadBook(book)

                filepath = os.path.join(download_dir, filename)
                with open(filepath, "wb") as bookfile:
                    bookfile.write(filecontent)

                progress.update(task, completed=True)

                console.print(
                    f"\n[green]✓ Successfully downloaded:[/green] " f"[cyan]{filepath}[/cyan]"
                )
                return filepath
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"\n[red]✗ Error downloading book: {e}[/red]")
                return None

    def show_download_menu(self) -> Optional[Literal["quit"]]:
        """Show download options after search"""
        if not self.current_results:
            return None

        console.print("\n[bold cyan]Download Options[/bold cyan]")

        choice = Prompt.ask(
            "\nWhat would you like to do?", choices=["download", "skip", "quit"], default="skip"
        )

        if choice == "download":
            book_num = IntPrompt.ask(
                f"Enter book number to download (1-{len(self.current_results)})", default=1
            )

            # Guard: validate book number
            book_num = max(1, min(len(self.current_results), book_num))

            book = self.current_results[book_num - 1]
            self.download_with_progress(book)
            return None
        elif choice == "quit":
            return "quit"
        return None

    def _confirm_proceed_with_search(self) -> bool:
        """Ask user to confirm proceeding with search. Returns False to exit, True to continue."""
        proceed = Confirm.ask("\n[cyan]Proceed with search?[/cyan]", default=True)
        if not proceed and not Confirm.ask("[yellow]Start a new search?[/yellow]", default=True):
            return False
        return proceed

    def _handle_search_cycle(self) -> bool:
        """Execute one search cycle. Returns False to exit loop, True to continue."""
        params = self.get_search_params()
        self.display_search_params(params)

        if not self._confirm_proceed_with_search():
            return False

        results = self.search_with_progress(params)

        if results and self.display_results_table(results):
            result = self.show_download_menu()
            if result == "quit":
                return False

        console.print()
        if not Confirm.ask("[cyan]Search for another book?[/cyan]", default=True):
            return False

        console.print("\n" + "=" * 70 + "\n")
        return True

    def _handle_keyboard_interrupt(self) -> bool:
        """Handle keyboard interrupt. Returns False to exit, True to continue."""
        console.print("\n\n[yellow]Search cancelled[/yellow]")
        return Confirm.ask("[cyan]Start a new search?[/cyan]", default=True)

    def _handle_exception(self, error: Exception) -> bool:
        """Handle general exception. Returns False to exit, True to continue."""
        console.print(f"\n[red]Error: {error}[/red]")
        return Confirm.ask("[cyan]Try again?[/cyan]", default=True)

    def run(self) -> None:
        """Main TUI loop"""
        self.show_welcome()

        while True:
            try:
                if not self._handle_search_cycle():
                    break
            except KeyboardInterrupt:
                if not self._handle_keyboard_interrupt():
                    break
            except Exception as e:
                if not self._handle_exception(e):
                    break

        console.print("\n[cyan]Goodbye![/cyan]\n")
