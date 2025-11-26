"""
Tool calling agent for integrating with MCP tools.
"""

from typing import Dict, Any
from ..services.mcp_client import mcp_client
from ..agents.supervisor import supervisor_agent
from ..repositories.employee_repository import get_employee_repository
from ..utils.database import get_db
from ..utils.exceptions import log_info, log_error


class ToolCallingAgent:
    """Agent responsible for calling MCP tools to provision accounts."""

    def __init__(self):
        """Initialize tool calling agent."""
        pass

    def provision_account(self, employee_id: str, account_type: str) -> Dict[str, Any]:
        """
        Provision an account for an employee.

        Args:
            employee_id: Employee ID
            account_type: Type of account to provision (email, git)

        Returns:
            Provisioning result
        """
        try:
            log_info(f"Provisioning {account_type} account for employee {employee_id}")

            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Get employee information
            employee = repo.get_employee(employee_id)
            if not employee:
                db.close()
                return {
                    'status': 'error',
                    'message': 'Employee not found'
                }

            # Call appropriate MCP service based on account type
            if account_type == 'email':
                result = mcp_client.provision_email_account(
                    employee_id, employee.first_name, employee.last_name)
            elif account_type == 'git':
                result = mcp_client.provision_git_account(
                    employee_id, employee.first_name, employee.last_name)
            else:
                db.close()
                return {
                    'status': 'error',
                    'message': f'Unsupported account type: {account_type}'
                }

            # Store account credentials if provisioning was successful
            if result.get('status') == 'success':
                credentials = repo.create_account_credentials(
                    employee_id, account_type, result.get('username', ''))

                # Update supervisor about completed step
                supervisor_agent.update_onboarding_step(employee_id, 'permissions_granted')

            db.close()

            return result

        except Exception as e:
            log_error(e, f"Failed to provision {account_type} account for employee {employee_id}")
            return {
                'status': 'error',
                'message': f"Failed to provision {account_type} account: {str(e)}"
            }

    def get_account_status(self, account_id: str) -> Dict[str, Any]:
        """
        Get the status of a provisioned account.

        Args:
            account_id: Account identifier

        Returns:
            Account status information
        """
        try:
            log_info(f"Getting account status for account {account_id}")
            return mcp_client.get_account_status(account_id)
        except Exception as e:
            log_error(e, f"Failed to get account status for account {account_id}")
            return {
                'status': 'error',
                'message': f"Failed to get account status: {str(e)}"
            }


# Global tool calling agent instance
tool_calling_agent = ToolCallingAgent()