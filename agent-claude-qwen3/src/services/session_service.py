"""
Session service for managing employee onboarding sessions.
"""

from typing import Dict, Any, Optional
from ..agents.supervisor import supervisor_agent
from ..utils.exceptions import log_info, log_error

class SessionService:
    """Service for managing onboarding sessions."""

    def __init__(self):
        """Initialize session service."""
        # In a real implementation, this might use a proper session store
        # For now, we'll keep it simple
        self.active_sessions = {}

    def create_session(self, first_name: str, last_name: str) -> Dict[str, Any]:
        """
        Create a new onboarding session.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name

        Returns:
            Session information
        """
        try:
            log_info(f"Creating session for {first_name} {last_name}")

            # Start onboarding through supervisor agent
            session_info = supervisor_agent.start_onboarding(first_name, last_name)

            if 'error' in session_info:
                return session_info

            # Store session
            session_id = session_info['session_id']
            self.active_sessions[session_id] = {
                'employee_id': session_info['employee_id'],
                'created_at': None  # In a real implementation, we'd store timestamp
            }

            return session_info

        except Exception as e:
            log_error(e, f"Failed to create session for {first_name} {last_name}")
            return {
                'error': f"Failed to create session: {str(e)}"
            }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Session information or None if not found
        """
        try:
            log_info(f"Retrieving session {session_id}")

            if session_id in self.active_sessions:
                # Get current status from supervisor
                employee_id = self.active_sessions[session_id]['employee_id']
                status = supervisor_agent.get_onboarding_status(employee_id)
                return status

            return None

        except Exception as e:
            log_error(e, f"Failed to get session {session_id}")
            return None

    def end_session(self, session_id: str) -> bool:
        """
        End an onboarding session.

        Args:
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        try:
            log_info(f"Ending session {session_id}")

            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return True

            return False

        except Exception as e:
            log_error(e, f"Failed to end session {session_id}")
            return False

    def is_session_active(self, session_id: str) -> bool:
        """
        Check if a session is active.

        Args:
            session_id: Session ID

        Returns:
            True if session is active, False otherwise
        """
        return session_id in self.active_sessions

# Global session service instance
session_service = SessionService()