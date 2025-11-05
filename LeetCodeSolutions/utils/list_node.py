"""Definition for singly-linked list node."""

from typing import Optional


class ListNode:
    """Singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        """String representation of the linked list."""
        vals = []
        current = self
        while current:
            vals.append(str(current.val))
            current = current.next
            if len(vals) > 100:  # Prevent infinite loops
                vals.append("...")
                break
        return " -> ".join(vals)

    @classmethod
    def from_list(cls, values: list[int]) -> Optional["ListNode"]:
        """Create a linked list from a Python list."""
        if not values:
            return None

        head = cls(values[0])
        current = head
        for val in values[1:]:
            current.next = cls(val)
            current = current.next
        return head

    def to_list(self) -> list[int]:
        """Convert linked list to Python list."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
            if len(result) > 100:  # Prevent infinite loops
                break
        return result
