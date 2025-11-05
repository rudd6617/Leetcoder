"""Definition for binary tree node."""

from collections import deque
from typing import Optional


class TreeNode:
    """Binary tree node."""

    def __init__(
        self,
        val: int = 0,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """String representation of the tree."""
        return f"TreeNode({self.val})"

    @classmethod
    def from_list(cls, values: list[int | None]) -> Optional["TreeNode"]:
        """
        Create a binary tree from level-order list representation.

        Example:
            [1, 2, 3, None, 4] creates:
                 1
                / \\
               2   3
                \\
                 4
        """
        if not values or values[0] is None:
            return None

        root = cls(values[0])
        queue = deque([root])
        i = 1

        while queue and i < len(values):
            node = queue.popleft()

            # Left child
            if i < len(values) and values[i] is not None:
                node.left = cls(values[i])
                queue.append(node.left)
            i += 1

            # Right child
            if i < len(values) and values[i] is not None:
                node.right = cls(values[i])
                queue.append(node.right)
            i += 1

        return root

    def to_list(self) -> list[int | None]:
        """Convert tree to level-order list representation."""
        if not self:
            return []

        result = []
        queue = deque([self])

        while queue:
            node = queue.popleft()
            if node:
                result.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append(None)

        # Remove trailing None values
        while result and result[-1] is None:
            result.pop()

        return result
