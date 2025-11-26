"""
Chinese ID number validation service according to GB 11643-1999 standard.
"""
import sys
import os
import re

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_id_number(id_number: str) -> bool:
    """
    Validate Chinese ID number according to GB 11643-1999 standard.

    Args:
        id_number (str): The 18-digit Chinese ID number to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Check if ID number is exactly 18 characters
    if not id_number or len(id_number) != 18:
        return False

    # Check if first 17 characters are digits and last character is digit or X
    if not re.match(r'^\d{17}[\dX]$', id_number):
        return False

    # Extract parts
    address_code = id_number[:6]
    birth_date = id_number[6:14]
    sequence_code = id_number[14:17]
    check_digit = id_number[17]

    # Validate birth date (YYYYMMDD format)
    try:
        year = int(birth_date[:4])
        month = int(birth_date[4:6])
        day = int(birth_date[6:8])

        # Basic date validation
        if not (1900 <= year <= 2099):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
    except ValueError:
        return False

    # Calculate check digit using ISO 7064:1983 MOD 11-2 algorithm
    # Weights for Chinese ID numbers: [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    total = sum(int(digit) * weight for digit, weight in zip(id_number[:17], weights))
    remainder = total % 11

    # Check digit mapping: 0=1, 1=0, 2=X, 3=9, 4=8, 5=7, 6=6, 7=5, 8=4, 9=3, 10=2
    check_digit_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    expected_check_digit = check_digit_map[remainder]

    return check_digit == expected_check_digit


def get_birth_date(id_number: str) -> str:
    """
    Extract birth date from Chinese ID number.

    Args:
        id_number (str): The 18-digit Chinese ID number

    Returns:
        str: Birth date in YYYY-MM-DD format

    Raises:
        ValueError: If ID number is invalid
    """
    if not validate_id_number(id_number):
        raise ValueError("Invalid ID number")

    birth_date = id_number[6:14]
    return f"{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:8]}"


def get_gender(id_number: str) -> str:
    """
    Determine gender from Chinese ID number.

    Args:
        id_number (str): The 18-digit Chinese ID number

    Returns:
        str: "male" or "female"

    Raises:
        ValueError: If ID number is invalid
    """
    if not validate_id_number(id_number):
        raise ValueError("Invalid ID number")

    # The 17th digit determines gender (odd for male, even for female)
    gender_digit = int(id_number[16])
    return "male" if gender_digit % 2 == 1 else "female"