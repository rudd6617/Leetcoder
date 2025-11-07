"""LeetCoder - Automated LeetCode problem tracker and solution manager."""

import argparse

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.database import Database
from src.leetcode_api import LeetCodeAPI
from src.problem_index import ProblemIndex
from src.solution_generator import SolutionGenerator

console = Console(force_terminal=True, legacy_windows=False)

# Difficulty color mapping
DIFFICULTY_COLORS = {
    "Easy": "green",
    "Medium": "yellow",
    "Hard": "red",
}


def get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level."""
    return DIFFICULTY_COLORS.get(difficulty, "white")


def add_problem(
    problem_ids: list[str],
    api: LeetCodeAPI,
    generator: SolutionGenerator,
    index: ProblemIndex,
):
    """
    Add one or more problems.

    Args:
        problem_ids: List of problem IDs or slugs
        api: LeetCode API client
        generator: Solution file generator
        index: Problem index manager
    """
    for pid in problem_ids:
        try:
            problem_data = None

            # Try to parse as integer (problem ID)
            try:
                problem_id = int(pid)
                # Try local database first
                problem_data = index.get_problem(problem_id)
                if not problem_data:
                    # Fall back to API
                    console.print(
                        f"[yellow][!] Problem {problem_id} not in local database. "
                        f"Fetching from LeetCode...[/yellow]"
                    )
                    problem_data = api.get_problem_by_id(problem_id)
            except ValueError:
                # It's a slug - try database first
                problem_data = index.db.get_problem_by_slug(pid)
                if not problem_data:
                    # Fall back to API
                    console.print(
                        f"[yellow][!] Problem '{pid}' not in local database. "
                        f"Fetching from LeetCode...[/yellow]"
                    )
                    problem_data = api.get_problem_by_slug(pid)

            if not problem_data:
                console.print(f"[red][X] Problem '{pid}' not found[/red]")
                console.print(
                    "[dim][*] Hint: Run 'uv run python main.py sync' to download all problems[/dim]"
                )
                continue

            # Check if already exists
            if index.problem_exists(problem_data["id"]):
                console.print(
                    f"[yellow][!] Problem {problem_data['id']} ({problem_data['title']}) "
                    f"already exists[/yellow]"
                )
                continue

            # Generate solution file
            filepath = generator.generate_solution_file(problem_data)

            # Add to index
            index.add_problem(problem_data, filepath.name)

            console.print(
                f"[green][OK] Added: {problem_data['id']}. {problem_data['title']} "
                f"({problem_data['difficulty']})[/green]"
            )

        except Exception as e:
            console.print(f"[red][X] Error adding problem '{pid}': {e}[/red]")


def search_problems(keyword: str, index: ProblemIndex, search_by_tag: bool = False):
    """
    Search problems by keyword or tag.

    Args:
        keyword: Search keyword
        index: Problem index manager
        search_by_tag: If True, search by tag instead of title
    """
    if search_by_tag:
        results = index.search_by_tag(keyword)
        search_type = "tag"
    else:
        results = index.search_by_title(keyword)
        search_type = "title"

    if not results:
        console.print(f"[yellow]No problems found with {search_type} '{keyword}'[/yellow]")
        return

    table = Table(title=f"Search Results: '{keyword}'", box=box.ROUNDED)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Difficulty", justify="center")
    table.add_column("Tags", style="dim")

    for problem in results:
        difficulty_color = get_difficulty_color(problem["difficulty"])

        table.add_row(
            str(problem["id"]),
            problem["title"],
            f"[{difficulty_color}]{problem['difficulty']}[/{difficulty_color}]",
            ", ".join(problem["tags"][:3]) + ("..." if len(problem["tags"]) > 3 else ""),
        )

    console.print(table)
    console.print(f"\nFound {len(results)} problem(s)")


def list_problems(index: ProblemIndex):
    """
    List all problems in the index.

    Args:
        index: Problem index manager
    """
    problems = index.get_all_problems()

    if not problems:
        console.print("[yellow]No problems added yet. Use 'add' command to get started.[/yellow]")
        return

    table = Table(title="All Problems", box=box.ROUNDED)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Difficulty", justify="center")
    table.add_column("Tags", style="dim")
    table.add_column("File", style="blue")

    for problem in problems:
        difficulty_color = get_difficulty_color(problem["difficulty"])

        table.add_row(
            str(problem["id"]),
            problem["title"],
            f"[{difficulty_color}]{problem['difficulty']}[/{difficulty_color}]",
            ", ".join(problem["tags"][:3]) + ("..." if len(problem["tags"]) > 3 else ""),
            problem["filename"],
        )

    console.print(table)
    console.print(f"\nTotal: {len(problems)} problem(s)")


def show_statistics(index: ProblemIndex):
    """
    Show statistics about solved problems.

    Args:
        index: Problem index manager
    """
    stats = index.get_statistics()

    if stats["total"] == 0:
        console.print("[yellow]No problems added yet.[/yellow]")
        return

    # Total problems
    console.print(Panel(f"[bold cyan]{stats['total']}[/bold cyan]", title="Total Problems"))

    # By difficulty
    if stats["by_difficulty"]:
        diff_table = Table(title="By Difficulty", box=box.SIMPLE)
        diff_table.add_column("Difficulty", style="white")
        diff_table.add_column("Count", justify="right", style="cyan")

        for difficulty in ["Easy", "Medium", "Hard"]:
            count = stats["by_difficulty"].get(difficulty, 0)
            if count > 0:
                color = get_difficulty_color(difficulty)
                diff_table.add_row(f"[{color}]{difficulty}[/{color}]", str(count))

        console.print(diff_table)

    # Top tags
    if stats["by_tag"]:
        tag_table = Table(title="Top 10 Tags", box=box.SIMPLE)
        tag_table.add_column("Tag", style="white")
        tag_table.add_column("Count", justify="right", style="cyan")

        for tag, count in stats["by_tag"].items():
            tag_table.add_row(tag, str(count))

        console.print(tag_table)


def sync_database(api: LeetCodeAPI, force: bool = False):
    """
    Sync all LeetCode problems to local database.

    Args:
        api: LeetCode API client
        force: If True, re-sync all problems (not just new ones)
    """
    db = Database()

    # Check current status
    status = db.get_sync_status()

    if status["total_problems"] > 0 and not force:
        console.print(
            f"\n[green][OK] Database already contains {status['total_problems']} problems[/green]"
        )
        console.print(f"[dim]Last synced: {status['last_sync']}[/dim]")
        console.print("\n[yellow]Use --force to re-sync all problems[/yellow]")
        db.close()
        return

    # Perform sync
    try:
        synced, skipped = api.sync_all_problems(db, skip_existing=not force)

        console.print("\n[green][OK] Sync complete![/green]")
        console.print(f"[cyan]   New problems synced: {synced}[/cyan]")
        if skipped > 0:
            console.print(f"[dim]   Skipped (already exists): {skipped}[/dim]")

        # Show final status
        status = db.get_sync_status()
        console.print(f"\n[bold]Total problems in database: {status['total_problems']}[/bold]")

    except Exception as e:
        console.print(f"\n[red][X] Sync failed: {e}[/red]")
    finally:
        db.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LeetCoder - Automated LeetCode problem tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sync               # Sync all problems to local database (first time)
  python main.py add 1              # Add problem by ID (from local database)
  python main.py add two-sum        # Add problem by slug
  python main.py add 1 2 15         # Add multiple problems
  python main.py search array       # Search by keyword
  python main.py search -t "Array"  # Search by tag
  python main.py list               # List all problems
  python main.py stats              # Show statistics

Workflow:
  1. Run 'sync' once to download all problems to local database
  2. Use 'add' to generate solution files (instant, no network needed)
  3. Use 'list', 'search', 'stats' to manage your progress
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add one or more problems")
    add_parser.add_argument("problems", nargs="+", help="Problem ID(s) or slug(s)")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search problems")
    search_parser.add_argument("keyword", help="Search keyword")
    search_parser.add_argument(
        "-t", "--tag", action="store_true", help="Search by tag instead of title"
    )

    # List command
    subparsers.add_parser("list", help="List all problems")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    # Sync command
    sync_parser = subparsers.add_parser(
        "sync", help="Sync all problems from LeetCode to local database"
    )
    sync_parser.add_argument("--force", action="store_true", help="Force re-sync all problems")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize components
    api = LeetCodeAPI()
    generator = SolutionGenerator()
    index = ProblemIndex()

    # Execute command
    if args.command == "add":
        add_problem(args.problems, api, generator, index)
    elif args.command == "search":
        search_problems(args.keyword, index, search_by_tag=args.tag)
    elif args.command == "list":
        list_problems(index)
    elif args.command == "stats":
        show_statistics(index)
    elif args.command == "sync":
        sync_database(api, force=args.force)


if __name__ == "__main__":
    main()
