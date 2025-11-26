from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Final

ADDRESS_CODE_PATTERN: Final = re.compile(r"^[1-9][0-9]{5}$")
ID_PATTERN: Final = re.compile(r"^[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]$")
WEIGHTS: Final = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
PARITY: Final = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]


class ValidationError(Exception):
    """Raised when a national ID fails validation."""


@dataclass
class ValidationResult:
    normalized_id: str
    address_code: str
    birth_date: dt.date
    sequence_code: str


def _validate_address_code(address_code: str) -> None:
    if not ADDRESS_CODE_PATTERN.match(address_code):
        raise ValidationError("Invalid address code")


def _validate_birth_date(date_str: str) -> dt.date:
    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    try:
        return dt.date(year, month, day)
    except ValueError as exc:
        raise ValidationError("Invalid birth date") from exc


def _validate_sequence_code(sequence: str) -> None:
    if sequence == "000":
        raise ValidationError("Sequence code cannot be 000")


def _calculate_checksum(id17: str) -> str:
    total = sum(int(num) * weight for num, weight in zip(id17, WEIGHTS))
    return PARITY[total % 11]


def validate_national_id(national_id: str) -> ValidationResult:
    if not ID_PATTERN.match(national_id):
        raise ValidationError("National ID format invalid")

    normalized = national_id.upper()
    address_code = normalized[:6]
    birth_date_str = normalized[6:14]
    sequence_code = normalized[14:17]
    checksum = normalized[-1]

    _validate_address_code(address_code)
    birth_date = _validate_birth_date(birth_date_str)
    _validate_sequence_code(sequence_code)

    expected_checksum = _calculate_checksum(normalized[:17])
    if checksum != expected_checksum:
        raise ValidationError("Checksum mismatch")

    return ValidationResult(
        normalized_id=normalized,
        address_code=address_code,
        birth_date=birth_date,
        sequence_code=sequence_code,
    )
