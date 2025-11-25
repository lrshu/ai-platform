"""Contract tests for the chat CLI command."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.chat import chat_command


def test_chat_command_contract():
    """Test the chat command contract."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, user_id=None):
            self.name = name
            self.user_id = user_id

    # Test with valid arguments
    args = MockArgs("test_doc", "test_user")

    # Mock the conversation manager
    with patch('src.cli.chat.conversation_manager') as mock_manager:
        mock_conversation = MagicMock()
        mock_conversation.id = "test_conversation_id"
        mock_manager.create_conversation.return_value = mock_conversation
        mock_manager.process_message.return_value = "This is a test response"
        mock_manager.end_conversation.return_value = None

        # Mock input to simulate user interaction
        with patch('builtins.input', side_effect=['Hello', 'exit']):
            # Call the chat command
            result = chat_command(args)

            # Verify the conversation manager was called correctly
            mock_manager.create_conversation.assert_called_once_with(
                user_id="test_user",
                document_name="test_doc"
            )
            mock_manager.process_message.assert_called_once_with(
                mock_conversation,
                "Hello"
            )
            mock_manager.end_conversation.assert_called_once_with(
                mock_conversation
            )

            # Verify the command returns success
            assert result == 0


def test_chat_command_with_default_user():
    """Test the chat command with default user ID."""
    # Mock arguments
    class MockArgs:
        def __init__(self, name, user_id=None):
            self.name = name
            self.user_id = user_id

    # Test with valid arguments and no user_id
    args = MockArgs("test_doc")

    # Mock the conversation manager
    with patch('src.cli.chat.conversation_manager') as mock_manager:
        mock_conversation = MagicMock()
        mock_conversation.id = "test_conversation_id"
        mock_manager.create_conversation.return_value = mock_conversation
        mock_manager.process_message.return_value = "This is a test response"
        mock_manager.end_conversation.return_value = None

        # Mock input to simulate user interaction
        with patch('builtins.input', side_effect=['Hello', 'exit']):
            # Call the chat command
            result = chat_command(args)

            # Verify the conversation manager was called correctly with default user
            mock_manager.create_conversation.assert_called_once_with(
                user_id="default_user",
                document_name="test_doc"
            )

            # Verify the command returns success
            assert result == 0


if __name__ == "__main__":
    pytest.main([__file__])