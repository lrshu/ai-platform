from __future__ import annotations

import re


class MarkdownParser:
    heading_pattern = re.compile(r"^(#+)\s+(.*)$", re.MULTILINE)

    def from_text(self, text: str) -> str:
        sanitized = text.replace("\r", "")
        if not sanitized.strip():
            return ""
        return self._normalize_headings(sanitized)

    def _normalize_headings(self, text: str) -> str:
        return self.heading_pattern.sub(lambda m: f"{m.group(1)} {m.group(2).strip()}", text)
