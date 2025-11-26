"""
Batch account provisioning service.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.account import BatchProvisioningRequest, BatchProvisioningResult, BatchProvisioningResponse, ProvisioningRequest
from services.email_provisioning_service import provision_email_account
from services.git_provisioning_service import provision_git_account


def provision_batch_accounts(request: BatchProvisioningRequest) -> BatchProvisioningResponse:
    """
    Provision multiple accounts in batch.

    Args:
        request (BatchProvisioningRequest): Request containing multiple provisioning requests

    Returns:
        BatchProvisioningResponse: Results of batch provisioning
    """
    results = []

    for item in request.requests:
        result = BatchProvisioningResult(
            name=item.name,
            id_number=item.id_number
        )

        try:
            # Provision accounts based on requested types
            accounts = []
            for account_type in item.account_types:
                provisioning_request = ProvisioningRequest(
                    name=item.name,
                    id_number=item.id_number
                )

                if account_type == "email":
                    account = provision_email_account(provisioning_request)
                    accounts.append(account)
                elif account_type == "git":
                    account = provision_git_account(provisioning_request)
                    accounts.append(account)

            # Convert accounts to response format
            result.accounts = [
                {"username": account.username, "password": account.password}
                for account in accounts
            ]
        except ValueError as e:
            result.error = str(e)
        except Exception as e:
            result.error = f"Internal error: {str(e)}"

        results.append(result)

    return BatchProvisioningResponse(results=results)