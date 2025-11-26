from __future__ import annotations

import secrets
import string

PASSWORD_LENGTH = 16
CHAR_GROUPS = {
    "upper": string.ascii_uppercase,
    "lower": string.ascii_lowercase,
    "digits": string.digits,
    "symbols": "@#%+=!",
}
ALL_CHARS = "".join(CHAR_GROUPS.values())


def generate_password() -> str:
    system_random = secrets.SystemRandom()
    password_chars = [system_random.choice(group) for group in CHAR_GROUPS.values()]
    remaining_length = PASSWORD_LENGTH - len(password_chars)
    password_chars.extend(system_random.choice(ALL_CHARS) for _ in range(remaining_length))
    system_random.shuffle(password_chars)
    return "".join(password_chars)
