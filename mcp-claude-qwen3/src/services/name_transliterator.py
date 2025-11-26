"""
Chinese name to English transliteration service using pypinyin.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypinyin import lazy_pinyin, Style


def transliterate_name(chinese_name: str) -> str:
    """
    Convert Chinese name to English transliteration.

    Args:
        chinese_name (str): The Chinese name to transliterate

    Returns:
        str: English transliteration of the name in lowercase
    """
    if not chinese_name:
        return ""

    # Use pypinyin to convert Chinese characters to pinyin
    # Style.NORMAL removes tone marks
    pinyin_list = lazy_pinyin(chinese_name, style=Style.NORMAL)

    # Join with underscores and convert to lowercase
    return "".join(pinyin_list).lower()


def format_email_username(chinese_name: str, domain: str = "email.com") -> str:
    """
    Format email username from Chinese name.

    Args:
        chinese_name (str): The Chinese name
        domain (str): The email domain

    Returns:
        str: Email address in format "english_name@domain"
    """
    english_name = transliterate_name(chinese_name)
    return f"{english_name}@{domain}"


def format_git_username(chinese_name: str) -> str:
    """
    Format git username from Chinese name.

    Args:
        chinese_name (str): The Chinese name

    Returns:
        str: Git username in format "english_name@git.com"
    """
    return format_email_username(chinese_name, "git.com")