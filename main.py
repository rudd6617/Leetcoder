"""LeetCoder - Automated LeetCode problem tracker and solution manager."""

import argparse

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.leetcode_api import LeetCodeAPI
from src.problem_index import ProblemIndex
from src.solution_generator import SolutionGenerator

console = Console()


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
            # Try to parse as integer (problem ID)
            try:
                problem_id = int(pid)
                problem_data = api.get_problem_by_id(problem_id)
            except ValueError:
                # It's a slug
                problem_data = api.get_problem_by_slug(pid)

            if not problem_data:
                console.print(f"[red]✗ Problem '{pid}' not found[/red]")
                continue

            # Check if already exists
            if index.problem_exists(problem_data["id"]):
                console.print(
                    f"[yellow]⚠ Problem {problem_data['id']} ({problem_data['title']}) "
                    f"already exists[/yellow]"
                )
                continue

            # Generate solution file
            filepath = generator.generate_solution_file(problem_data)

            # Add to index
            index.add_problem(problem_data, filepath.name)

            console.print(
                f"[green]✓ Added: {problem_data['id']}. {problem_data['title']} "
                f"({problem_data['difficulty']})[/green]"
            )

        except Exception as e:
            console.print(f"[red]✗ Error adding problem '{pid}': {e}[/red]")


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
        difficulty_color = {
            "Easy": "green",
            "Medium": "yellow",
            "Hard": "red",
        }.get(problem["difficulty"], "white")

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
        difficulty_color = {
            "Easy": "green",
            "Medium": "yellow",
            "Hard": "red",
        }.get(problem["difficulty"], "white")

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
                color = {"Easy": "green", "Medium": "yellow", "Hard": "red"}[difficulty]
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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LeetCoder - Automated LeetCode problem tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py add 1              # Add problem by ID
  python main.py add two-sum        # Add problem by slug
  python main.py add 1 2 15         # Add multiple problems
  python main.py search array       # Search by keyword
  python main.py search -t "Array"  # Search by tag
  python main.py list               # List all problems
  python main.py stats              # Show statistics
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


if __name__ == "__main__":
    main()
