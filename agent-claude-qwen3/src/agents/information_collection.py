"""
Information collection agent for gathering employee details.
"""

from typing import Dict, Any, List
from ..models import EducationLevel
from ..repositories.employee_repository import get_employee_repository
from ..agents.supervisor import supervisor_agent
from ..utils.database import get_db
from ..utils.exceptions import ValidationError, log_info, log_error

class InformationCollectionAgent:
    """Agent responsible for collecting employee information."""

    def __init__(self):
        """Initialize information collection agent."""
        pass

    def request_employee_information(self, employee_id: str) -> Dict[str, Any]:
        """
        Request employee to provide personal information.

        Args:
            employee_id: Employee ID

        Returns:
            Information collection form
        """
        try:
            log_info(f"Requesting employee information for {employee_id}")

            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Get employee data
            employee = repo.get_employee(employee_id)
            if not employee:
                db.close()
                return {'error': 'Employee not found'}

            db.close()

            return {
                'employee_id': employee_id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'fields': [
                    {
                        'name': 'school',
                        'label': 'Graduated School/Institution',
                        'type': 'text',
                        'required': True,
                        'placeholder': 'Enter the name of your school or institution'
                    },
                    {
                        'name': 'education_level',
                        'label': 'Education Level',
                        'type': 'select',
                        'required': True,
                        'options': [
                            {'value': 'HIGH_SCHOOL', 'label': 'High School'},
                            {'value': 'ASSOCIATE', 'label': 'Associate Degree'},
                            {'value': 'BACHELOR', 'label': 'Bachelor\'s Degree'},
                            {'value': 'MASTER', 'label': 'Master\'s Degree'},
                            {'value': 'DOCTORATE', 'label': 'Doctorate'},
                            {'value': 'OTHER', 'label': 'Other'}
                        ]
                    },
                    {
                        'name': 'position',
                        'label': 'Job Position',
                        'type': 'select',
                        'required': True,
                        'options': [
                            {'value': 'software_engineer', 'label': 'Software Engineer'},
                            {'value': 'product_manager', 'label': 'Product Manager'},
                            {'value': 'hr_specialist', 'label': 'HR Specialist'},
                            {'value': 'admin_assistant', 'label': 'Administrative Assistant'}
                        ]
                    }
                ],
                'next_step': 'collect_information'
            }

        except Exception as e:
            log_error(e, f"Failed to request employee information for {employee_id}")
            return {
                'error': f"Failed to request employee information: {str(e)}"
            }

    def validate_employee_information(self, employee_id: str, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate collected employee information.

        Args:
            employee_id: Employee ID
            information: Collected information

        Returns:
            Validation result
        """
        try:
            log_info(f"Validating employee information for {employee_id}")

            errors = []

            # Validate school
            school = information.get('school', '').strip()
            if not school:
                errors.append({'field': 'school', 'message': 'School/Institution is required'})

            # Validate education level
            education_level = information.get('education_level')
            if not education_level:
                errors.append({'field': 'education_level', 'message': 'Education level is required'})
            elif education_level not in [level.value for level in EducationLevel]:
                errors.append({'field': 'education_level', 'message': 'Invalid education level'})

            # Validate position
            position = information.get('position')
            if not position:
                errors.append({'field': 'position', 'message': 'Job position is required'})

            if errors:
                return {
                    'valid': False,
                    'errors': errors
                }
            else:
                return {
                    'valid': True,
                    'errors': []
                }

        except Exception as e:
            log_error(e, f"Failed to validate employee information for {employee_id}")
            return {
                'valid': False,
                'errors': [{'field': 'general', 'message': f"Validation error: {str(e)}"}]
            }

    def process_employee_information(self, employee_id: str, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and store validated employee information.

        Args:
            employee_id: Employee ID
            information: Validated information

        Returns:
            Processing result
        """
        try:
            log_info(f"Processing employee information for {employee_id}")

            # Validate information first
            validation_result = self.validate_employee_information(employee_id, information)
            if not validation_result['valid']:
                return validation_result

            # Get database session and repository
            db = next(get_db())
            repo = get_employee_repository(db)

            # Update employee with collected information
            update_fields = {
                'school': information.get('school', '').strip(),
                'education_level': information.get('education_level'),
                'position': information.get('position')
            }

            employee = repo.update_employee(employee_id, **update_fields)

            if not employee:
                db.close()
                return {
                    'valid': False,
                    'errors': [{'field': 'general', 'message': 'Employee not found'}]
                }

            # Update supervisor about completed step
            supervisor_agent.update_onboarding_step(employee_id, 'information_collected')

            db.close()

            return {
                'valid': True,
                'message': 'Information collected successfully',
                'next_step': 'show_responsibilities'
            }

        except Exception as e:
            log_error(e, f"Failed to process employee information for {employee_id}")
            return {
                'valid': False,
                'errors': [{'field': 'general', 'message': f"Processing error: {str(e)}"}]
            }

    def handle_validation_errors(self, employee_id: str, errors: List[Dict]) -> Dict[str, Any]:
        """
        Handle validation errors and provide feedback.

        Args:
            employee_id: Employee ID
            errors: List of validation errors

        Returns:
            Feedback with error details
        """
        try:
            log_info(f"Handling validation errors for {employee_id}")

            return {
                'employee_id': employee_id,
                'status': 'validation_error',
                'errors': errors,
                'message': 'Please correct the following errors and try again',
                'next_step': 'correct_information'
            }

        except Exception as e:
            log_error(e, f"Failed to handle validation errors for {employee_id}")
            return {
                'error': f"Failed to handle validation errors: {str(e)}"
            }

# Global information collection agent instance
information_collection_agent = InformationCollectionAgent()