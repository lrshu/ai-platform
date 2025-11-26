"""
Git account provisioning service.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.account import Account, ProvisioningRequest
from services.id_validator import validate_id_number
from services.name_transliterator import format_git_username
from services.password_generator import generate_secure_password
from datetime import datetime


def provision_git_account(request: ProvisioningRequest) -> Account:
    """
    Provision a git account for an employee.

    Args:
        request (ProvisioningRequest): Request containing name and ID number

    Returns:
        Account: Provisioned git account

    Raises:
        ValueError: If ID number is invalid
    """
    # Validate ID number
    if not validate_id_number(request.id_number):
        raise ValueError("Invalid ID number format")

    # Generate git username
    username = format_git_username(request.name)

    # Generate secure password
    password = generate_secure_password()

    # Create account
    account = Account(
        username=username,
        password=password,
        account_type="git",
        created_at=datetime.now()
    )

    return account