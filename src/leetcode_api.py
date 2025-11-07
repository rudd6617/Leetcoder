"""LeetCode GraphQL API client for fetching problem information."""

import time

import requests
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn


class LeetCodeAPI:
    """Client for interacting with LeetCode GraphQL API."""

    GRAPHQL_URL = "https://leetcode.com/graphql"
    PROBLEM_URL = "https://leetcode.com/problems/{slug}/"

    def __init__(self):
        """Initialize the API client."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
            }
        )
        # Cache for ID -> slug mapping to avoid repeated API calls
        self._id_to_slug_cache: dict[int, str] = {}
        self._cache_loaded = False

    def get_problem_by_slug(self, slug: str) -> dict | None:
        """
        Get problem details by problem slug.

        Args:
            slug: Problem slug (e.g., "two-sum")

        Returns:
            Dictionary containing problem information or None if not found
        """
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                exampleTestcases
                topicTags {
                    name
                    slug
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                hints
            }
        }
        """

        variables = {"titleSlug": slug}
        payload = {"query": query, "variables": variables}

        try:
            response = self.session.post(self.GRAPHQL_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                return None

            question = data.get("data", {}).get("question")
            if not question:
                return None

            return self._format_problem_data(question)

        except requests.exceptions.RequestException:
            return None

    def _load_id_to_slug_cache(self):
        """Load ID to slug mapping cache (called once)."""
        if self._cache_loaded:
            return

        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                questions: data {
                    questionFrontendId
                    titleSlug
                }
            }
        }
        """

        variables = {
            "categorySlug": "",
            "skip": 0,
            "limit": 3000,
            "filters": {},
        }
        payload = {"query": query, "variables": variables}

        try:
            response = self.session.post(self.GRAPHQL_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            questions = data.get("data", {}).get("problemsetQuestionList", {}).get("questions", [])

            # Build cache: int ID -> slug
            for q in questions:
                frontend_id = q.get("questionFrontendId")
                slug = q.get("titleSlug")
                if frontend_id and slug:
                    self._id_to_slug_cache[int(frontend_id)] = slug

            self._cache_loaded = True

        except requests.exceptions.RequestException:
            pass

    def get_problem_by_id(self, problem_id: int) -> dict | None:
        """
        Get problem details by problem frontend ID.

        Args:
            problem_id: Problem frontend ID (e.g., 1 for "Two Sum")

        Returns:
            Dictionary containing problem information or None if not found
        """
        # Load cache on first call (lazy loading)
        self._load_id_to_slug_cache()

        # Lookup slug from cache
        slug = self._id_to_slug_cache.get(problem_id)
        if not slug:
            return None

        return self.get_problem_by_slug(slug)

    def close(self):
        """Close the HTTP session and release resources."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def _format_problem_data(self, question: dict) -> dict:
        """Format raw GraphQL response into structured problem data."""
        # Get Python code snippet
        python_snippet = ""
        code_snippets = question.get("codeSnippets") or []
        for snippet in code_snippets:
            if snippet.get("langSlug") == "python3":
                python_snippet = snippet.get("code", "")
                break

        return {
            "id": int(question.get("questionFrontendId", 0)),
            "title": question.get("title", ""),
            "slug": question.get("titleSlug", ""),
            "difficulty": question.get("difficulty", ""),
            "content": question.get("content", ""),
            "tags": [tag["name"] for tag in (question.get("topicTags") or [])],
            "hints": question.get("hints") or [],
            "code_snippet": python_snippet,
            "url": self.PROBLEM_URL.format(slug=question.get("titleSlug", "")),
        }

    def sync_all_problems(self, db, skip_existing: bool = True):
        """
        Sync all LeetCode problems to database.

        Args:
            db: Database instance
            skip_existing: If True, skip problems already in database

        Returns:
            Number of problems synced
        """
        # First, load the ID-to-slug cache if not already loaded
        self._load_id_to_slug_cache()

        total = len(self._id_to_slug_cache)
        synced_count = 0
        skipped_count = 0

        print(f"\n🔄 Syncing {total} problems from LeetCode...")
        print("⏳ This may take 2-5 minutes. Please be patient.\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Syncing problems...", total=total)

            for problem_id, slug in self._id_to_slug_cache.items():
                # Check if already exists
                if skip_existing:
                    existing = db.get_problem(problem_id)
                    if existing:
                        skipped_count += 1
                        progress.advance(task)
                        continue

                # Fetch full problem details
                try:
                    problem_data = self.get_problem_by_slug(slug)
                    if problem_data:
                        db.upsert_problem(problem_data)
                        synced_count += 1

                    # Rate limiting: be nice to LeetCode servers
                    time.sleep(0.1)

                except Exception:
                    # Continue on error, don't interrupt sync
                    pass

                progress.advance(task)

        return synced_count, skipped_count
