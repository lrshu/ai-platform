"""
Integration tests for the employee onboarding system.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_main_import():
    """Test that main module can be imported without errors."""
    try:
        import main
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import main module: {e}")

def test_main_no_args(capsys):
    """Test main function with no arguments."""
    from main import main

    # Mock sys.argv to simulate no arguments
    with patch('sys.argv', ['main.py']):
        main()

        # Capture printed output
        captured = capsys.readouterr()
        # Should show help message
        assert "usage:" in captured.out.lower()

def test_main_chat_mode(capsys):
    """Test main function with chat mode."""
    from main import main

    # Mock sys.argv to simulate chat mode
    with patch('sys.argv', ['main.py', 'chat']):
        main()

        # Capture printed output
        captured = capsys.readouterr()
        # Should show chat mode message
        assert "welcome to the employee onboarding system" in captured.out.lower()

def test_main_serve_mode(capsys):
    """Test main function with serve mode."""
    from main import main

    # Mock sys.argv to simulate serve mode
    with patch('sys.argv', ['main.py', 'serve']):
        main()

        # Capture printed output
        captured = capsys.readouterr()
        # Should show serve mode message
        assert "starting employee onboarding rest api server" in captured.out.lower()

if __name__ == "__main__":
    pytest.main([__file__])