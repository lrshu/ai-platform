"""Checklist management helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ChecklistItem(str, Enum):
    """Checklist steps for the onboarding flow."""

    ID_VERIFICATION = "identity_verification"
    INFO_COMPLETION = "information_completion"
    ROLE_BRIEFING = "role_briefing"
    ACCESS_SETUP = "access_setup"
    FINAL_GUIDANCE = "final_guidance"


@dataclass
class Checklist:
    """Track checklist state in-memory."""

    status: Dict[ChecklistItem, bool] = field(
        default_factory=lambda: {item: False for item in ChecklistItem}
    )

    def mark_done(self, item: ChecklistItem) -> None:
        self.status[item] = True

    def is_done(self, item: ChecklistItem) -> bool:
        return self.status.get(item, False)

    def summary(self) -> List[str]:
        return [f"{item.value}: {'✅' if done else '⏳'}" for item, done in self.status.items()]
