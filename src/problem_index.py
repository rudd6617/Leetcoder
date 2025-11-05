"""Manage local index of LeetCode problems."""

import json
from collections import Counter
from pathlib import Path


class ProblemIndex:
    """Manage and query the local problem index."""

    def __init__(self, index_file: str = "data/problems.json"):
        """
        Initialize the problem index.

        Args:
            index_file: Path to the JSON index file
        """
        self.index_path = Path(index_file)
        self.index_path.parent.mkdir(exist_ok=True)
        self.problems = self._load_index()

    def _load_index(self) -> dict:
        """Load the problem index from file."""
        if self.index_path.exists():
            try:
                with open(self.index_path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in {self.index_path}, creating new index")
                return {}
        return {}

    def _save_index(self):
        """Save the problem index to file."""
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self.problems, f, indent=2, ensure_ascii=False)

    def add_problem(self, problem_data: dict, filename: str):
        """
        Add a problem to the index.

        Args:
            problem_data: Problem information from API
            filename: Generated filename for the problem
        """
        problem_id = str(problem_data["id"])

        self.problems[problem_id] = {
            "id": problem_data["id"],
            "title": problem_data["title"],
            "slug": problem_data["slug"],
            "difficulty": problem_data["difficulty"],
            "tags": problem_data["tags"],
            "filename": filename,
            "url": problem_data["url"],
        }

        self._save_index()

    def get_problem(self, problem_id: int) -> dict | None:
        """
        Get problem information by ID.

        Args:
            problem_id: Problem number

        Returns:
            Problem data or None if not found
        """
        return self.problems.get(str(problem_id))

    def problem_exists(self, problem_id: int) -> bool:
        """
        Check if a problem is already in the index.

        Args:
            problem_id: Problem number

        Returns:
            True if problem exists, False otherwise
        """
        return str(problem_id) in self.problems

    def search_by_title(self, keyword: str) -> list[dict]:
        """
        Search problems by title keyword.

        Args:
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching problems
        """
        keyword = keyword.lower()
        results = []

        for problem in self.problems.values():
            if keyword in problem["title"].lower() or keyword in problem["slug"].lower():
                results.append(problem)

        return sorted(results, key=lambda x: x["id"])

    def search_by_tag(self, tag: str) -> list[dict]:
        """
        Search problems by tag.

        Args:
            tag: Tag name (case-insensitive)

        Returns:
            List of matching problems
        """
        tag = tag.lower()
        results = []

        for problem in self.problems.values():
            problem_tags = [t.lower() for t in problem["tags"]]
            if tag in problem_tags:
                results.append(problem)

        return sorted(results, key=lambda x: x["id"])

    def get_all_problems(self) -> list[dict]:
        """
        Get all problems in the index.

        Returns:
            List of all problems, sorted by ID
        """
        return sorted(self.problems.values(), key=lambda x: x["id"])

    def get_statistics(self) -> dict:
        """
        Get statistics about solved problems.

        Returns:
            Dictionary with statistics
        """
        if not self.problems:
            return {
                "total": 0,
                "by_difficulty": {},
                "by_tag": {},
            }

        difficulties = Counter(p["difficulty"] for p in self.problems.values())
        all_tags = []
        for p in self.problems.values():
            all_tags.extend(p["tags"])
        tag_counts = Counter(all_tags)

        return {
            "total": len(self.problems),
            "by_difficulty": dict(difficulties),
            "by_tag": dict(tag_counts.most_common(10)),  # Top 10 tags
        }

    def clear_index(self):
        """Clear all problems from the index."""
        self.problems = {}
        self._save_index()
