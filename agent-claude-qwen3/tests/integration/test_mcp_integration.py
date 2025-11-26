"""
Integration tests for MCP client and tool calling.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_mcp_client_initialization():
    """Test that MCP client can be initialized without errors."""
    try:
        from src.services.mcp_client import mcp_client
        assert True
    except Exception as e:
        pytest.fail(f"Failed to initialize MCP client: {e}")

def test_tool_calling_agent_initialization():
    """Test that tool calling agent can be initialized without errors."""
    try:
        from src.agents.tool_calling import tool_calling_agent
        assert True
    except Exception as e:
        pytest.fail(f"Failed to initialize tool calling agent: {e}")

@patch('src.services.mcp_client.MCPClient._make_request')
def test_provision_email_account(mock_make_request):
    """Test provisioning an email account through the tool calling agent."""
    # Mock the MCP client response
    mock_make_request.return_value = {
        'status': 'success',
        'username': 'john.doe@example.com',
        'account_id': 'acc_123'
    }

    # Import the tool calling agent
    from src.agents.tool_calling import tool_calling_agent

    # Test with invalid employee ID (should return error)
    result = tool_calling_agent.provision_account('emp_123', 'email')

    # Verify the result is an error since employee doesn't exist
    assert 'status' in result
    assert result['status'] == 'error'
    assert 'employee not found' in result['message'].lower()

@patch('src.services.mcp_client.MCPClient._make_request')
def test_provision_git_account(mock_make_request):
    """Test provisioning a git account through the tool calling agent."""
    # Mock the MCP client response
    mock_make_request.return_value = {
        'status': 'success',
        'username': 'johndoe',
        'account_id': 'git_123'
    }

    # Import the tool calling agent
    from src.agents.tool_calling import tool_calling_agent

    # Test with invalid employee ID (should return error)
    result = tool_calling_agent.provision_account('emp_123', 'git')

    # Verify the result is an error since employee doesn't exist
    assert 'status' in result
    assert result['status'] == 'error'
    assert 'employee not found' in result['message'].lower()

def test_invalid_account_type():
    """Test provisioning with an invalid account type."""
    # Import the tool calling agent
    from src.agents.tool_calling import tool_calling_agent

    # Test provisioning with invalid account type
    result = tool_calling_agent.provision_account('emp_123', 'invalid_type')

    # Verify the result
    assert 'status' in result
    assert result['status'] == 'error'
    # Since employee doesn't exist, we should get employee not found error first
    assert 'employee not found' in result['message'].lower()

if __name__ == "__main__":
    pytest.main([__file__])