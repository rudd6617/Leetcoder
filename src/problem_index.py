"""Manage local index of LeetCode problems using SQLite."""

import json
from pathlib import Path

from src.database import Database


class ProblemIndex:
    """Manage and query the local problem index using SQLite."""

    def __init__(self, db_path: str = "data/leetcode.db", solutions_dir: str = "LeetCodeSolutions"):
        """
        Initialize the problem index.

        Args:
            db_path: Path to the SQLite database file
            solutions_dir: Directory where solution files are stored
        """
        self.db = Database(db_path)
        self.solutions_dir = Path(solutions_dir)

    def add_problem(self, problem_data: dict, filename: str):
        """
        Add a problem to the index.

        Args:
            problem_data: Problem information from API or database
            filename: Generated filename for the problem
        """
        # Mark as added in database
        self.db.mark_as_added(problem_data["id"], filename)

    def get_problem(self, problem_id: int) -> dict | None:
        """
        Get problem information by ID.

        Args:
            problem_id: Problem number

        Returns:
            Problem data or None if not found
        """
        return self.db.get_problem(problem_id)

    def problem_exists(self, problem_id: int) -> bool:
        """
        Check if a problem is already added.

        Args:
            problem_id: Problem number

        Returns:
            True if problem is added and file exists, False otherwise
        """
        if not self.db.is_added(problem_id):
            return False

        # Get filename from database
        filename = self.db.get_added_filename(problem_id)
        if not filename:
            return False

        filepath = self.solutions_dir / filename
        return filepath.exists()

    def search_by_title(self, keyword: str) -> list[dict]:
        """
        Search added problems by title keyword.

        Args:
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching problems
        """
        return self.db.search_added_by_title(keyword)

    def search_by_tag(self, tag: str) -> list[dict]:
        """
        Search added problems by tag.

        Args:
            tag: Tag name (case-insensitive)

        Returns:
            List of matching problems
        """
        return self.db.search_added_by_tag(tag)

    def get_all_problems(self) -> list[dict]:
        """
        Get all added problems.

        Returns:
            List of all problems, sorted by ID
        """
        return self.db.get_all_added_problems()

    def get_statistics(self) -> dict:
        """
        Get statistics about added problems.

        Returns:
            Dictionary with statistics
        """
        return self.db.get_statistics()

    def close(self):
        """Close database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
