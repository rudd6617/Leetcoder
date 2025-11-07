"""SQLite database management for LeetCode problems."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    """Manage SQLite database for LeetCode problems."""

    def __init__(self, db_path: str = "data/leetcode.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Problems table - stores all LeetCode problems
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                difficulty TEXT NOT NULL,
                content TEXT NOT NULL,
                code_snippet TEXT NOT NULL,
                tags TEXT NOT NULL,
                hints TEXT,
                url TEXT NOT NULL,
                synced_at TEXT NOT NULL
            )
        """)

        # Added problems table - tracks user-generated files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS added_problems (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                added_at TEXT NOT NULL,
                FOREIGN KEY (id) REFERENCES problems(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slug ON problems(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_difficulty ON problems(difficulty)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON problems(title)")

        conn.commit()

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def upsert_problem(self, problem_data: dict):
        """
        Insert or update a problem.

        Args:
            problem_data: Problem data from LeetCode API
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO problems
            (id, title, slug, difficulty, content, code_snippet, tags, hints, url, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                problem_data["id"],
                problem_data["title"],
                problem_data["slug"],
                problem_data["difficulty"],
                problem_data["content"],
                problem_data["code_snippet"],
                json.dumps(problem_data["tags"]),
                json.dumps(problem_data.get("hints", [])),
                problem_data["url"],
                datetime.now().isoformat(),
            ),
        )

        conn.commit()

    def get_problem(self, problem_id: int) -> dict | None:
        """
        Get problem by ID.

        Args:
            problem_id: Problem ID

        Returns:
            Problem data or None if not found
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def get_problem_by_slug(self, slug: str) -> dict | None:
        """
        Get problem by slug.

        Args:
            slug: Problem slug

        Returns:
            Problem data or None if not found
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM problems WHERE slug = ?", (slug,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def search_by_title(self, keyword: str) -> list[dict]:
        """
        Search problems by title keyword.

        Args:
            keyword: Search keyword

        Returns:
            List of matching problems
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM problems
            WHERE title LIKE ? OR slug LIKE ?
            ORDER BY id
        """,
            (f"%{keyword}%", f"%{keyword}%"),
        )

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_by_tag(self, tag: str) -> list[dict]:
        """
        Search problems by tag.

        Args:
            tag: Tag name

        Returns:
            List of matching problems
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM problems
            WHERE tags LIKE ?
            ORDER BY id
        """,
            (f"%{tag}%",),
        )

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def mark_as_added(self, problem_id: int, filename: str):
        """
        Mark a problem as added (file generated).

        Args:
            problem_id: Problem ID
            filename: Generated filename
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO added_problems (id, filename, added_at)
            VALUES (?, ?, ?)
        """,
            (problem_id, filename, datetime.now().isoformat()),
        )

        conn.commit()

    def is_added(self, problem_id: int) -> bool:
        """
        Check if problem is already added.

        Args:
            problem_id: Problem ID

        Returns:
            True if added, False otherwise
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM added_problems WHERE id = ?", (problem_id,))
        return cursor.fetchone() is not None

    def get_added_filename(self, problem_id: int) -> str | None:
        """
        Get the filename for an added problem.

        Args:
            problem_id: Problem ID

        Returns:
            Filename if problem is added, None otherwise
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT filename FROM added_problems WHERE id = ?", (problem_id,))
        row = cursor.fetchone()
        return row["filename"] if row else None

    def get_all_added_problems(self) -> list[dict]:
        """
        Get all added problems.

        Returns:
            List of added problems with their details
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.*, a.filename, a.added_at
            FROM problems p
            JOIN added_problems a ON p.id = a.id
            ORDER BY p.id
        """
        )

        results = []
        for row in cursor.fetchall():
            problem = self._row_to_dict(row)
            problem["filename"] = row["filename"]
            results.append(problem)

        return results

    def search_added_by_title(self, keyword: str) -> list[dict]:
        """
        Search added problems by title keyword.

        Args:
            keyword: Search keyword

        Returns:
            List of matching added problems
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.*, a.filename, a.added_at
            FROM problems p
            JOIN added_problems a ON p.id = a.id
            WHERE p.title LIKE ? OR p.slug LIKE ?
            ORDER BY p.id
        """,
            (f"%{keyword}%", f"%{keyword}%"),
        )

        results = []
        for row in cursor.fetchall():
            problem = self._row_to_dict(row)
            problem["filename"] = row["filename"]
            results.append(problem)

        return results

    def search_added_by_tag(self, tag: str) -> list[dict]:
        """
        Search added problems by tag.

        Args:
            tag: Tag name

        Returns:
            List of matching added problems
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.*, a.filename, a.added_at
            FROM problems p
            JOIN added_problems a ON p.id = a.id
            WHERE p.tags LIKE ?
            ORDER BY p.id
        """,
            (f"%{tag}%",),
        )

        results = []
        for row in cursor.fetchall():
            problem = self._row_to_dict(row)
            problem["filename"] = row["filename"]
            results.append(problem)

        return results

    def get_statistics(self) -> dict:
        """
        Get statistics about added problems.

        Returns:
            Statistics dictionary
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) as count FROM added_problems")
        total = cursor.fetchone()["count"]

        # By difficulty
        cursor.execute(
            """
            SELECT p.difficulty, COUNT(*) as count
            FROM problems p
            JOIN added_problems a ON p.id = a.id
            GROUP BY p.difficulty
        """
        )
        by_difficulty = {row["difficulty"]: row["count"] for row in cursor.fetchall()}

        # By tag (top 10)
        cursor.execute(
            """
            SELECT p.tags
            FROM problems p
            JOIN added_problems a ON p.id = a.id
        """
        )
        all_tags = []
        for row in cursor.fetchall():
            tags = json.loads(row["tags"])
            all_tags.extend(tags)

        from collections import Counter

        tag_counts = Counter(all_tags)

        return {
            "total": total,
            "by_difficulty": by_difficulty,
            "by_tag": dict(tag_counts.most_common(10)),
        }

    def get_sync_status(self) -> dict:
        """
        Get sync status of the database.

        Returns:
            Dictionary with total problems and last sync time
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM problems")
        total = cursor.fetchone()["count"]

        cursor.execute("SELECT MAX(synced_at) as last_sync FROM problems")
        last_sync = cursor.fetchone()["last_sync"]

        return {"total_problems": total, "last_sync": last_sync}

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert SQLite row to dictionary."""
        data = dict(row)
        # Parse JSON fields
        if "tags" in data:
            data["tags"] = json.loads(data["tags"])
        if "hints" in data and data["hints"]:
            data["hints"] = json.loads(data["hints"])
        return data
