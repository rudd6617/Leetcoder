"""LeetCode GraphQL API client for fetching problem information."""

import requests


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
                print(f"GraphQL errors: {data['errors']}")
                return None

            question = data.get("data", {}).get("question")
            if not question:
                return None

            return self._format_problem_data(question)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching problem: {e}")
            return None

    def get_problem_by_id(self, problem_id: int) -> dict | None:
        """
        Get problem details by problem frontend ID.

        Args:
            problem_id: Problem frontend ID (e.g., 1 for "Two Sum")

        Returns:
            Dictionary containing problem information or None if not found
        """
        # First, we need to get all problems to find the slug by ID
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

            # Find the slug for this problem ID
            for q in questions:
                if q.get("questionFrontendId") == str(problem_id):
                    slug = q.get("titleSlug")
                    return self.get_problem_by_slug(slug)

            print(f"Problem with ID {problem_id} not found")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching problem list: {e}")
            return None

    def _format_problem_data(self, question: dict) -> dict:
        """Format raw GraphQL response into structured problem data."""
        # Get Python code snippet
        python_snippet = ""
        for snippet in question.get("codeSnippets", []):
            if snippet.get("langSlug") == "python3":
                python_snippet = snippet.get("code", "")
                break

        return {
            "id": int(question.get("questionFrontendId", 0)),
            "title": question.get("title", ""),
            "slug": question.get("titleSlug", ""),
            "difficulty": question.get("difficulty", ""),
            "content": question.get("content", ""),
            "tags": [tag["name"] for tag in question.get("topicTags", [])],
            "hints": question.get("hints", []),
            "code_snippet": python_snippet,
            "url": self.PROBLEM_URL.format(slug=question.get("titleSlug", "")),
        }
