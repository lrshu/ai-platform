"""
Supervisor agent for orchestrating the employee onboarding process.
"""

from typing import Dict, Optional, Any
from ..models import OnboardingStatus
from ..repositories.employee_repository import get_employee_repository
from ..utils.database import get_db
from ..utils.exceptions import log_info, log_error
from ..services.id_verification_service import id_verification_service
from ..services.position_service import position_service
from ..services.mcp_client import mcp_client

class SupervisorAgent:
    """Main supervisor agent that orchestrates the onboarding process."""

    def __init__(self):
        """Initialize supervisor agent."""
        self.current_employee_id = None
        self.current_step = None

    def start_onboarding(self, first_name: str, last_name: str) -> Dict[str, Any]:
        """
        Start the onboarding process for a new employee.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name

        Returns:
            Onboarding session information
        """
        try:
            log_info(f"Starting onboarding for {first_name} {last_name}")

            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Create employee record
            employee = repo.create_employee(first_name, last_name)

            # Store current employee ID
            self.current_employee_id = employee.id

            # Set initial onboarding status
            repo.update_employee(employee.id, onboarding_status=OnboardingStatus.ID_UPLOAD_PENDING.value)

            # Get onboarding checklist
            checklist = repo.get_onboarding_checklist(employee.id)

            # Extract checklist data before closing the session
            checklist_data = {
                'id': checklist.id,
                'identity_verified': checklist.identity_verified,
                'information_collected': checklist.information_collected,
                'responsibilities_shown': checklist.responsibilities_shown,
                'permissions_granted': checklist.permissions_granted,
                'post_tasks_reminded': checklist.post_tasks_reminded,
                'completed': checklist.completed
            }

            db.close()

            return {
                'session_id': employee.id,
                'employee_id': employee.id,
                'checklist': checklist_data,
                'next_step': 'upload_id_photo'
            }

        except Exception as e:
            log_error(e, f"Failed to start onboarding for {first_name} {last_name}")
            return {
                'error': f"Failed to start onboarding: {str(e)}"
            }

    def get_onboarding_status(self, employee_id: str) -> Dict[str, Any]:
        """
        Get current onboarding status for an employee.

        Args:
            employee_id: Employee ID

        Returns:
            Onboarding status information
        """
        try:
            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Get employee and checklist
            employee = repo.get_employee(employee_id)
            if not employee:
                db.close()
                return {'error': 'Employee not found'}

            checklist = repo.get_onboarding_checklist(employee_id)
            if not checklist:
                db.close()
                return {'error': 'Onboarding checklist not found'}

            # Determine next step
            next_step = self._determine_next_step(checklist)

            db.close()

            return {
                'employee_id': employee_id,
                'onboarding_status': employee.onboarding_status,
                'checklist': {
                    'id': checklist.id,
                    'identity_verified': checklist.identity_verified,
                    'information_collected': checklist.information_collected,
                    'responsibilities_shown': checklist.responsibilities_shown,
                    'permissions_granted': checklist.permissions_granted,
                    'post_tasks_reminded': checklist.post_tasks_reminded,
                    'completed': checklist.completed
                },
                'next_step': next_step
            }

        except Exception as e:
            log_error(e, f"Failed to get onboarding status for employee {employee_id}")
            return {
                'error': f"Failed to get onboarding status: {str(e)}"
            }

    def _determine_next_step(self, checklist) -> str:
        """
        Determine the next step in the onboarding process.

        Args:
            checklist: Onboarding checklist

        Returns:
            Next step identifier
        """
        if not checklist.identity_verified:
            return 'upload_id_photo'
        elif not checklist.information_collected:
            return 'collect_information'
        elif not checklist.responsibilities_shown:
            return 'show_responsibilities'
        elif not checklist.permissions_granted:
            return 'grant_permissions'
        elif not checklist.post_tasks_reminded:
            return 'remind_post_tasks'
        elif not checklist.completed:
            return 'complete_onboarding'
        else:
            return 'onboarding_complete'

    def update_onboarding_step(self, employee_id: str, step: str, **kwargs) -> Dict[str, Any]:
        """
        Update onboarding step completion.

        Args:
            employee_id: Employee ID
            step: Step that was completed
            **kwargs: Additional data for the step

        Returns:
            Updated onboarding status
        """
        try:
            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Update checklist based on completed step
            update_fields = {}
            status_update = None

            if step == 'identity_verified':
                update_fields['identity_verified'] = True
                status_update = OnboardingStatus.INFORMATION_COLLECTION.value
            elif step == 'information_collected':
                update_fields['information_collected'] = True
                status_update = OnboardingStatus.RESPONSIBILITIES_REVIEW.value
            elif step == 'responsibilities_shown':
                update_fields['responsibilities_shown'] = True
                status_update = OnboardingStatus.PERMISSIONS_PROVISIONING.value
            elif step == 'permissions_granted':
                update_fields['permissions_granted'] = True
                status_update = OnboardingStatus.COMPLETED.value
            elif step == 'post_tasks_reminded':
                update_fields['post_tasks_reminded'] = True
            elif step == 'completed':
                update_fields['completed'] = True

            # Update checklist
            repo.update_onboarding_checklist(employee_id, **update_fields)

            # Update employee status if needed
            if status_update:
                repo.update_employee(employee_id, onboarding_status=status_update)

            # Get updated status
            result = self.get_onboarding_status(employee_id)

            db.close()

            return result

        except Exception as e:
            log_error(e, f"Failed to update onboarding step {step} for employee {employee_id}")
            return {
                'error': f"Failed to update onboarding step: {str(e)}"
            }

    def complete_onboarding(self, employee_id: str) -> Dict[str, Any]:
        """
        Mark onboarding as complete and provide post-onboarding tasks.

        Args:
            employee_id: Employee ID

        Returns:
            Completion information with post-onboarding tasks
        """
        try:
            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Get employee to check position
            employee = repo.get_employee(employee_id)
            if not employee:
                db.close()
                return {'error': 'Employee not found'}

            # Get post-onboarding tasks based on position
            tasks = position_service.get_post_onboarding_tasks(employee.position or "general")

            # Update checklist to mark onboarding as complete
            self.update_onboarding_step(employee_id, 'completed')

            db.close()

            return {
                'completed': True,
                'post_tasks': tasks
            }

        except Exception as e:
            log_error(e, f"Failed to complete onboarding for employee {employee_id}")
            return {
                'error': f"Failed to complete onboarding: {str(e)}"
            }

# Global supervisor agent instance
supervisor_agent = SupervisorAgent()