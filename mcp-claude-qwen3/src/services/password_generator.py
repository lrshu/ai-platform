"""
Secure password generation service using Python's secrets module.
"""
import sys
import os
import secrets
import string

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length (int): Length of the password (minimum 12 characters)

    Returns:
        str: Generated secure password
    """
    if length < 12:
        length = 12

    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ensure password contains at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]

    # Fill the rest of the password length with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))

    # Shuffle the password to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)