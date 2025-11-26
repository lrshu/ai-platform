"""
MCP client for tool calling and account provisioning.
"""

import requests
import json
from typing import Dict, Any, Optional
from ..utils.config import get_config
from ..utils.exceptions import ExternalServiceError, log_error, log_info

class MCPClient:
    """Client for interacting with MCP tools."""

    def __init__(self):
        """Initialize MCP client with configuration."""
        config = get_config()
        self.mcp_server = config.get('MCP_SERVER', 'http://127.0.0.1:9012/mcp')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[Any, Any]] = None) -> Dict[Any, Any]:
        """
        Make a request to the MCP server.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data as dictionary

        Raises:
            ExternalServiceError: If the request fails
        """
        url = f"{self.mcp_server}/{endpoint.lstrip('/')}"

        try:
            log_info(f"Making {method} request to {url}")

            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ExternalServiceError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            log_error(e, f"MCP request failed: {url}")
            raise ExternalServiceError(f"Failed to communicate with MCP server: {str(e)}")
        except json.JSONDecodeError as e:
            log_error(e, f"Invalid JSON response from MCP: {url}")
            raise ExternalServiceError(f"Invalid response from MCP server: {str(e)}")

    def provision_email_account(self, employee_id: str, first_name: str, last_name: str) -> Dict[Any, Any]:
        """
        Provision an email account for an employee.

        Args:
            employee_id: Employee identifier
            first_name: Employee first name
            last_name: Employee last name

        Returns:
            Provisioning response
        """
        data = {
            'employee_id': employee_id,
            'first_name': first_name,
            'last_name': last_name,
            'account_type': 'email'
        }

        return self._make_request('POST', '/accounts/provision', data)

    def provision_git_account(self, employee_id: str, first_name: str, last_name: str) -> Dict[Any, Any]:
        """
        Provision a git account for an employee.

        Args:
            employee_id: Employee identifier
            first_name: Employee first name
            last_name: Employee last name

        Returns:
            Provisioning response
        """
        data = {
            'employee_id': employee_id,
            'first_name': first_name,
            'last_name': last_name,
            'account_type': 'git'
        }

        return self._make_request('POST', '/accounts/provision', data)

    def get_account_status(self, account_id: str) -> Dict[Any, Any]:
        """
        Get the status of a provisioned account.

        Args:
            account_id: Account identifier

        Returns:
            Account status information
        """
        return self._make_request('GET', f'/accounts/{account_id}/status')

# Global MCP client instance
mcp_client = MCPClient()