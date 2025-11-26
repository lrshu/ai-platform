import os
import sys
from typing import List

REQUIRED_KEYS: List[str] = [
    "QWEN_API_BASE",
    "QWEN_API_KEY",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "MCP_SERVER",
]

def main() -> int:
    missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    if missing:
        missing_str = ", ".join(missing)
        print(f"Missing required environment variables: {missing_str}")
        return 1
    print("All required environment variables are set.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
