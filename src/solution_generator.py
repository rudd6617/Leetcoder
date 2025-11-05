"""Generate solution files for LeetCode problems."""

import re
from html.parser import HTMLParser
from pathlib import Path


class HTMLToTextParser(HTMLParser):
    """Convert HTML to plain text, preserving structure."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.in_pre = False
        self.in_strong = False

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.in_pre = True
            self.text.append("\n")
        elif tag == "strong":
            self.in_strong = True
        elif tag == "p" or tag == "ul":
            self.text.append("\n")
        elif tag == "li":
            self.text.append("\n- ")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False
            self.text.append("\n")
        elif tag == "strong":
            self.in_strong = False
        elif tag in ["p", "ul"]:
            self.text.append("\n")

    def handle_data(self, data):
        if data.strip():
            self.text.append(data)

    def get_text(self):
        text = "".join(self.text)
        # Clean up excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


class SolutionGenerator:
    """Generate Python solution files for LeetCode problems."""

    def __init__(self, solutions_dir: str = "LeetCodeSolutions"):
        """
        Initialize the solution generator.

        Args:
            solutions_dir: Directory where solution files will be created
        """
        self.solutions_dir = Path(solutions_dir)
        self.solutions_dir.mkdir(exist_ok=True)

    def generate_filename(self, problem_id: int, slug: str) -> str:
        """
        Generate filename for a problem.

        Args:
            problem_id: Problem number
            slug: Problem slug

        Returns:
            Filename in format p{id}_{slug}.py
        """
        # Format ID with leading zeros (4 digits)
        formatted_id = f"{problem_id:04d}"
        # Clean slug: replace hyphens with underscores
        clean_slug = slug.replace("-", "_")
        return f"p{formatted_id}_{clean_slug}.py"

    def html_to_text(self, html: str) -> str:
        """Convert HTML content to plain text."""
        parser = HTMLToTextParser()
        parser.feed(html)
        return parser.get_text()

    def extract_function_signature(self, code_snippet: str) -> dict:
        """
        Extract function name and signature from code snippet.

        Args:
            code_snippet: Python code snippet from LeetCode

        Returns:
            Dictionary with function_name and full signature
        """
        # Match function definition
        pattern = r"def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[^:]+)?:"
        match = re.search(pattern, code_snippet)

        if match:
            full_match = match.group(0).rstrip(":")
            func_name = match.group(1)
            return {"name": func_name, "signature": full_match}

        # Fallback
        return {"name": "solution", "signature": "def solution(self)"}

    def generate_solution_file(self, problem_data: dict) -> Path:
        """
        Generate a solution file for a problem.

        Args:
            problem_data: Problem data from LeetCode API

        Returns:
            Path to the generated file
        """
        filename = self.generate_filename(problem_data["id"], problem_data["slug"])
        filepath = self.solutions_dir / filename

        # Check if file already exists
        if filepath.exists():
            print(f"File {filename} already exists. Skipping...")
            return filepath

        # Convert HTML content to text
        description = self.html_to_text(problem_data["content"])

        # Extract function signature
        func_info = self.extract_function_signature(problem_data["code_snippet"])

        # Get imports from code snippet
        imports = self._extract_imports(problem_data["code_snippet"])

        # Generate file content
        content = self._generate_file_content(
            problem_data=problem_data,
            description=description,
            func_info=func_info,
            imports=imports,
        )

        # Write file
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ Created: {filename}")
        return filepath

    def _extract_imports(self, code_snippet: str) -> list[str]:
        """Extract import statements from code snippet."""
        imports = []
        for line in code_snippet.split("\n"):
            line = line.strip()
            if line.startswith("from ") or line.startswith("import "):
                imports.append(line)
        return imports

    def _generate_file_content(
        self, problem_data: dict, description: str, func_info: dict, imports: list[str]
    ) -> str:
        """Generate the complete file content."""
        problem_id = problem_data["id"]
        title = problem_data["title"]
        difficulty = problem_data["difficulty"]
        tags = ", ".join(problem_data["tags"])
        url = problem_data["url"]

        # Build imports section
        imports_section = "\n".join(imports) if imports else "from typing import List"

        template = f'''"""
LeetCode {problem_id}. {title}

Difficulty: {difficulty}
Tags: {tags}

{description}

Link: {url}
"""

{imports_section}


class Solution:
    """Solution for {title}."""

    {func_info["signature"]}:
        """
        TODO: Add solution description

        Args:
            TODO: Describe parameters

        Returns:
            TODO: Describe return value

        Time Complexity: O(?)
        Space Complexity: O(?)
        """
        pass


if __name__ == "__main__":
    # Test cases
    sol = Solution()

    # TODO: Add test cases
    # Example:
    # result = sol.{func_info["name"]}(...)
    # assert result == expected
    # print("✅ All test cases passed!")

    print("⚠️  Add your test cases above")
'''

        return template
