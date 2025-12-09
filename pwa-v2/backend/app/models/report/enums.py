"""
Report Enums Module

Defines enumerations for report-related fields.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from enum import Enum


class ReportStatus(str, Enum):
    """
    Report status enumeration.

    States:
    - DRAFT: Report is being created/edited
    - COMPLETED: Report is finalized but active
    - ARCHIVED: Report is archived (read-only)
    """

    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def list_values(cls) -> list[str]:
        """Get list of all status values."""
        return [status.value for status in cls]

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """
        Check if status transition is allowed.

        Allowed transitions:
        - draft -> completed
        - draft -> archived
        - completed -> archived
        - archived -> completed (unarchive)

        Args:
            from_status: Current status
            to_status: Target status

        Returns:
            bool: True if transition is allowed

        Example:
            >>> ReportStatus.can_transition("draft", "completed")
            True
            >>> ReportStatus.can_transition("archived", "draft")
            False
        """
        allowed_transitions = {
            cls.DRAFT: [cls.COMPLETED, cls.ARCHIVED],
            cls.COMPLETED: [cls.ARCHIVED],
            cls.ARCHIVED: [cls.COMPLETED],
        }

        current = cls(from_status)
        target = cls(to_status)

        return target in allowed_transitions.get(current, [])
