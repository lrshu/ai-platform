"""
Email account provisioning service.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.account import Account, ProvisioningRequest
from services.id_validator import validate_id_number
from services.name_transliterator import format_email_username
from services.password_generator import generate_secure_password
from datetime import datetime


def provision_email_account(request: ProvisioningRequest) -> Account:
    """
    Provision an email account for an employee.

    Args:
        request (ProvisioningRequest): Request containing name and ID number

    Returns:
        Account: Provisioned email account

    Raises:
        ValueError: If ID number is invalid
    """
    # Validate ID number
    if not validate_id_number(request.id_number):
        raise ValueError("Invalid ID number format")

    # Generate email username
    username = format_email_username(request.name, "email.com")

    # Generate secure password
    password = generate_secure_password()

    # Create account
    account = Account(
        username=username,
        password=password,
        account_type="email",
        created_at=datetime.now()
    )

    return account